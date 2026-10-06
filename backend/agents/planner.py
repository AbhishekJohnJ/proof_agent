from typing import List, Dict, Any
from backend.models.analysis import AnalysisPlan
from backend.providers.base import LLMProvider

class QueryPlanner:
    """Analytical Query Planner evaluating feasibility and constructing execution plans."""

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def create_plan(self, question: str, dataset_schemas: List[Dict[str, Any]], document_summaries: List[Dict[str, Any]]) -> AnalysisPlan:
        # LLM provider produces raw plan dict
        plan_dict = self.llm_provider.plan_query(question, dataset_schemas, document_summaries)

        return AnalysisPlan(
            query_type=plan_dict.get("query_type", "data_aggregation"),
            datasets_required=plan_dict.get("datasets_required", []),
            documents_required=plan_dict.get("documents_required", []),
            operations=plan_dict.get("operations", []),
            needs_code=plan_dict.get("needs_code", True),
            needs_retrieval=plan_dict.get("needs_retrieval", False),
            is_unanswerable=plan_dict.get("is_unanswerable", False),
            ambiguity_flags=plan_dict.get("ambiguity_flags", []),
            refusal_reason=plan_dict.get("refusal_reason")
        )
