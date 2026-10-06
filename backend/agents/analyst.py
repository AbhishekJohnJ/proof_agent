from typing import Dict, Any, List
from backend.providers.base import LLMProvider

class DataAnalystAgent:
    """Agent synthesizing human-readable final answers strictly matching canonical execution outputs."""

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def synthesize_answer(self, question: str, execution_result: Dict[str, Any], evidence_items: List[Any]) -> str:
        parsed = execution_result.get("parsed_output", {})
        if isinstance(parsed, dict) and "result" in parsed:
            val = parsed["result"]
            metric = parsed.get("metric", "value")
            unit = parsed.get("unit")
            unit_str = f" {unit}" if unit else ""

            return f"The calculated {metric} is {val}{unit_str}."

        stdout = execution_result.get("stdout")
        if stdout:
            return f"Verified calculation output: {stdout}"

        return "Analysis completed."
