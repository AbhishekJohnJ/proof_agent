from typing import Dict, Any, List
from backend.providers.base import LLMProvider

class DataAnalystAgent:
    """Agent responsible for analytical reasoning and query synthesis."""

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def synthesize_answer(self, question: str, execution_result: Dict[str, Any], evidence_items: List[Any]) -> str:
        parsed = execution_result.get("parsed_output", {})
        if parsed and "result" in parsed:
            val = parsed["result"]
            metric = parsed.get("metric", "value")
            return f"The calculated {metric} is {val}."

        if execution_result.get("stdout"):
            return f"Calculated result: {execution_result['stdout']}"

        return "Analysis completed successfully."
