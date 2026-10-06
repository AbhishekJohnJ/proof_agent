from typing import List, Dict, Any
from backend.models.analysis import AnalysisPlan
from backend.providers.base import LLMProvider

class QueryPlanner:
    """Analytical Query Planner evaluating feasibility, data availability, and constructing execution plans."""

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def create_plan(self, question: str, dataset_schemas: List[Dict[str, Any]], document_summaries: List[Dict[str, Any]]) -> AnalysisPlan:
        q_lower = question.lower()

        # Deterministic Refusal Check 1: Missing columns/metrics
        if dataset_schemas:
            all_column_names = []
            for ds in dataset_schemas:
                all_column_names.extend([c.lower() for c in ds.get("column_names", [])])

            if "profit" in q_lower or "margin" in q_lower:
                if not any(col in all_column_names for col in ["profit", "net_profit", "margin", "cost"]):
                    return AnalysisPlan(
                        query_type="unanswerable",
                        datasets_required=[],
                        documents_required=[],
                        operations=[],
                        needs_code=False,
                        needs_retrieval=False,
                        is_unanswerable=True,
                        ambiguity_flags=["missing_profit_data"],
                        refusal_reason="insufficient_data"
                    )

            if "tax" in q_lower or "deduction" in q_lower:
                if not any(col in all_column_names for col in ["tax", "vat", "deduction"]):
                    return AnalysisPlan(
                        query_type="unanswerable",
                        datasets_required=[],
                        documents_required=[],
                        operations=[],
                        needs_code=False,
                        needs_retrieval=False,
                        is_unanswerable=True,
                        ambiguity_flags=["missing_tax_data"],
                        refusal_reason="insufficient_data"
                    )

        # Delegate to LLM Provider
        plan_dict = self.llm_provider.plan_query(question, dataset_schemas, document_summaries)

        # Normalize operations format (support string list or dict list)
        raw_ops = plan_dict.get("operations", [])
        formatted_ops = []
        for op in raw_ops:
            if isinstance(op, str):
                formatted_ops.append({"type": op})
            elif isinstance(op, dict):
                formatted_ops.append(op)

        return AnalysisPlan(
            query_type=plan_dict.get("query_type", "data_aggregation"),
            datasets_required=plan_dict.get("datasets_required", []),
            documents_required=plan_dict.get("documents_required", []),
            operations=formatted_ops,
            needs_code=plan_dict.get("needs_code", True),
            needs_retrieval=plan_dict.get("needs_retrieval", False),
            is_unanswerable=plan_dict.get("is_unanswerable", False),
            ambiguity_flags=plan_dict.get("ambiguity_flags", []),
            refusal_reason=plan_dict.get("refusal_reason")
        )
