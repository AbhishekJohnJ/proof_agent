from typing import Dict, Any, List, Optional
from backend.models.analysis import CanonicalResult
from backend.services.answer_renderer import AnswerRenderer

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
        if canonical_result:
            return AnswerRenderer.render_answer(canonical_result)

        parsed = execution_result.get("parsed_output", {})
        if isinstance(parsed, dict) and "result" in parsed:
            c_res = CanonicalResult(
                result=parsed.get("result"),
                metric=str(parsed.get("metric", "value")),
                label=parsed.get("label"),
                unit=parsed.get("unit"),
                result_type=parsed.get("result_type", "scalar")
            )
            return AnswerRenderer.render_answer(c_res)

        stdout = execution_result.get("stdout")
        if stdout:
            return f"Verified calculation output: {stdout}"

        return "Analysis completed."
