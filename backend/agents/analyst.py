from typing import Dict, Any, List, Optional
from backend.models.analysis import CanonicalResult

class DataAnalystAgent:
    """Agent synthesizing human-readable final answers strictly matching canonical execution outputs."""

    def __init__(self, llm_provider: Optional[Any] = None):
        self.llm_provider = llm_provider

    def synthesize_answer(
        self,
        question: str,
        execution_result: Dict[str, Any],
        evidence_items: List[Any],
        canonical_result: Optional[CanonicalResult] = None
    ) -> str:
        # Priority 1: Use CanonicalResult if provided
        if canonical_result:
            val = canonical_result.result
            metric = canonical_result.metric or "value"
            label = canonical_result.label
            unit = canonical_result.unit

            unit_prefix = "₹" if unit == "INR" else ("$" if unit == "USD" else ("€" if unit == "EUR" else ""))
            unit_suffix = "%" if unit == "percent" else (f" {unit}" if unit and unit not in ["INR", "USD", "EUR"] else "")

            if label:
                return f"The highest {metric.replace('_', ' ')} is {label} with {unit_prefix}{val}{unit_suffix}."
            else:
                return f"The {metric.replace('_', ' ')} is {unit_prefix}{val}{unit_suffix}."

        parsed = execution_result.get("parsed_output", {})
        if isinstance(parsed, dict) and "result" in parsed:
            val = parsed["result"]
            metric = str(parsed.get("metric", "value"))
            unit = parsed.get("unit")
            unit_prefix = "₹" if unit == "INR" else ("$" if unit == "USD" else ("€" if unit == "EUR" else ""))
            unit_suffix = "%" if unit == "percent" else (f" {unit}" if unit and unit not in ["INR", "USD", "EUR"] else "")

            return f"The {metric.replace('_', ' ')} is {unit_prefix}{val}{unit_suffix}."

        stdout = execution_result.get("stdout")
        if stdout:
            return f"Verified calculation output: {stdout}"

        return "Analysis completed."
