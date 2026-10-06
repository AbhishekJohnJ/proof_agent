from typing import Any, Dict, List
from backend.providers.base import LLMProvider

class MockLLMProvider(LLMProvider):
    """Mock LLM Provider for local development & model-independent testing."""

    def __init__(self, model_name: str = "mock-qwen3-4b"):
        self.model_name = model_name

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> str:
        return f"[MOCK LLM GENERATION: {self.model_name}] Plan generated for prompt."

    def plan_query(self, question: str, dataset_schemas: List[Dict[str, Any]], document_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        question_lower = question.lower()

        # Handle unanswerable / trap question mocks
        if "profit" in question_lower and not any("profit" in str(s) for s in dataset_schemas):
            return {
                "query_type": "unanswerable",
                "datasets_required": [],
                "documents_required": [],
                "operations": [],
                "needs_code": False,
                "needs_retrieval": False,
                "is_unanswerable": True,
                "ambiguity_flags": ["missing_profit_data"],
                "refusal_reason": "insufficient_data"
            }

        return {
            "query_type": "data_aggregation",
            "datasets_required": [s.get("dataset_id", "ds_1") for s in dataset_schemas],
            "documents_required": [d.get("document_id", "doc_1") for d in document_summaries],
            "operations": ["filter", "aggregate"],
            "needs_code": True,
            "needs_retrieval": len(document_summaries) > 0,
            "is_unanswerable": False,
            "ambiguity_flags": [],
            "refusal_reason": None
        }
