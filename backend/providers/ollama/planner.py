import json
import re
import time
from typing import List, Dict, Any, Optional
from backend.providers.base import LLMProvider
from backend.providers.ollama.client import OllamaClient
from backend.providers.ollama.config import ollama_config
from backend.data.dataset_resolver import DatasetResolver
from backend.data.catalog import dataset_catalog
from backend.providers.ollama.exceptions import (
    OllamaUnavailableError,
    ModelNotFoundError,
    StructuredOutputValidationError
)

class OllamaPlanner(LLMProvider):
    """
    Production Query Planner backed by local Qwen3 model via Ollama.
    Enforces strict JSON formatting, dataset resolution, column validation,
    and structured retries without guessing or hallucinating schemas.
    """

    SYSTEM_PROMPT = """You are the Lead Analytical Planner for ProofAI (HNX26PSI08).
Your job is to analyze user analytical questions and construct a strict, executable AnalysisContract JSON.

CRITICAL RULES:
1. You MUST reason ONLY over the provided Authorized Datasets and Column Profiles.
2. DO NOT invent non-existent column names, table names, or metrics.
3. If the required data or column is missing from the authorized schemas, you MUST respond with "query_type": "unanswerable", "is_unanswerable": true, and a clear "refusal_reason".
4. Return ONLY valid, raw JSON conforming strictly to the requested schema. Do NOT wrap output in markdown fences (```json ... ```) or add commentary.

JSON SCHEMA FORMAT:
{
    "query_type": "data_aggregation" | "unanswerable" | "retrieval_augmented",
    "datasets_required": ["ds_orders"],
    "documents_required": [],
    "columns_required": ["final_amount"],
    "operations": [
        {"type": "aggregate", "column": "final_amount", "operation": "sum"}
    ],
    "joins": [
        {"left_dataset": "ds_orders", "right_dataset": "ds_customers", "left_column": "customer_id", "right_column": "customer_id", "how": "inner"}
    ],
    "filters": [
        {"column": "order_status", "operator": "==", "value": "DELIVERED"}
    ],
    "group_by": [
        {"column": "state"}
    ],
    "aggregations": [
        {"operation": "sum", "column": "final_amount"}
    ],
    "sorting": [
        {"column": "final_amount", "order": "desc"}
    ],
    "limit": 1,
    "expected_metric": "total_revenue",
    "expected_unit": "INR",
    "return_definition": null | "order_return_rate" | "item_return_rate" | "revenue_return_rate",
    "needs_code": true,
    "needs_retrieval": false,
    "is_unanswerable": false,
    "ambiguity_flags": [],
    "refusal_reason": null
}
"""

    def __init__(self, model_name: Optional[str] = None, client: Optional[OllamaClient] = None):
        self.model_name = model_name or ollama_config.planner_model
        self.client = client or OllamaClient()

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        res = self.client.generate(
            model=self.model_name,
            prompt=prompt,
            system_prompt=system_prompt or self.SYSTEM_PROMPT,
            json_format=True
        )
        return res.get("response", "")

    def _format_schema_prompt(
        self,
        dataset_schemas: List[Dict[str, Any]],
        document_summaries: List[Dict[str, Any]]
    ) -> str:
        lines = ["AUTHORIZED DATASETS AND SCHEMA DEFINITIONS:"]
        for s in dataset_schemas:
            ds_id = s.get("dataset_id") or s.get("name") or "ds_unknown"
            fname = s.get("filename", "")
            cols = s.get("column_names", [])
            types = s.get("dtypes", {})
            lines.append(f"\nDataset ID: {ds_id} (file: {fname})")
            lines.append("  Columns:")
            for col in cols:
                ctype = types.get(col, "unknown")
                lines.append(f"    - {col}: {ctype}")

        if document_summaries:
            lines.append("\nAUTHORIZED DOCUMENTS:")
            for d in document_summaries:
                lines.append(f"  Document ID: {d.get('doc_id')}, Title: {d.get('title')}")

        return "\n".join(lines)

    def _extract_json(self, raw_text: str) -> Dict[str, Any]:
        text = raw_text.strip()
        # Remove potential markdown fences
        if "```" in text:
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
            if match:
                text = match.group(1)
            else:
                text = re.sub(r"```(?:json)?|```", "", text).strip()
        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try finding first { and last }
            first = text.find("{")
            last = text.rfind("}")
            if first != -1 and last != -1 and last > first:
                snippet = text[first:last+1]
                return json.loads(snippet)
            raise

    def plan_query(
        self,
        question: str,
        dataset_schemas: List[Dict[str, Any]],
        document_summaries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Executes Qwen3 planning with schema validation, retry loop, and dataset resolution.
        """
        schema_text = self._format_schema_prompt(dataset_schemas, document_summaries)
        user_prompt = f"{schema_text}\n\nUSER QUESTION:\n{question}\n\nConstruct the AnalysisContract JSON:"

        last_error = None
        current_prompt = user_prompt

        start_time = time.perf_counter()

        for attempt in range(1, ollama_config.max_retries + 1):
            try:
                res = self.client.generate(
                    model=self.model_name,
                    prompt=current_prompt,
                    system_prompt=self.SYSTEM_PROMPT,
                    json_format=True,
                    temperature=0.0
                )
                raw_response = res.get("response", "")
                plan_dict = self._extract_json(raw_response)

                # Attach provenance
                latency_ms = int((time.perf_counter() - start_time) * 1000)
                plan_dict["_provenance"] = {
                    "provider": "ollama",
                    "model": self.model_name,
                    "latency_ms": res.get("latency_ms", latency_ms)
                }

                # Check if model chose refusal
                if plan_dict.get("is_unanswerable") or plan_dict.get("query_type") == "unanswerable":
                    plan_dict["query_type"] = "unanswerable"
                    plan_dict["is_unanswerable"] = True
                    return plan_dict

                # Validate dataset names against DatasetResolver
                req_ds = plan_dict.get("datasets_required", [])
                validated_ds = []
                for ds in req_ds:
                    resolved_id = dataset_catalog.resolve_dataset_by_name(ds)
                    if resolved_id:
                        validated_ds.append(resolved_id)
                    else:
                        # Attempt strict match in dataset_schemas
                        match_schema = next((s for s in dataset_schemas if s.get("dataset_id") == ds or s.get("filename") == ds or s.get("dataset_id") == f"ds_{ds}"), None)
                        if match_schema:
                            validated_ds.append(match_schema.get("dataset_id"))
                        else:
                            # Dataset resolution failed
                            return {
                                "query_type": "unanswerable",
                                "datasets_required": [],
                                "documents_required": [],
                                "operations": [],
                                "needs_code": False,
                                "is_unanswerable": True,
                                "ambiguity_flags": [f"unresolved_dataset:{ds}"],
                                "refusal_reason": f"Requested dataset '{ds}' is not authorized or available in catalog.",
                                "_provenance": plan_dict["_provenance"]
                            }

                if validated_ds:
                    plan_dict["datasets_required"] = list(dict.fromkeys(validated_ds))

                # Validate columns against authorized schemas
                all_valid_cols = set()
                for s in dataset_schemas:
                    for col in s.get("column_names", []):
                        all_valid_cols.add(col.lower())

                req_cols = plan_dict.get("columns_required", [])
                invalid_cols = [c for c in req_cols if c.lower() not in all_valid_cols and c != "*"]
                if invalid_cols:
                    return {
                        "query_type": "unanswerable",
                        "datasets_required": [],
                        "documents_required": [],
                        "operations": [],
                        "needs_code": False,
                        "is_unanswerable": True,
                        "ambiguity_flags": [f"invalid_column:{col}" for col in invalid_cols],
                        "refusal_reason": f"Requested column(s) {invalid_cols} do not exist in authorized dataset schema.",
                        "_provenance": plan_dict["_provenance"]
                    }

                return plan_dict

            except Exception as e:
                last_error = str(e)
                # Structured correction prompt for retry
                current_prompt = (
                    f"{user_prompt}\n\n"
                    f"ATTEMPT {attempt} FAILED WITH ERROR: {last_error}\n"
                    "Fix the JSON syntax or schema violations and return strictly valid JSON:"
                )

        # Retries exhausted
        return {
            "query_type": "unanswerable",
            "datasets_required": [],
            "documents_required": [],
            "operations": [],
            "needs_code": False,
            "is_unanswerable": True,
            "ambiguity_flags": ["llm_retry_exhausted"],
            "refusal_reason": f"Qwen3 model failed to output valid AnalysisContract after {ollama_config.max_retries} retries: {last_error}"
        }
