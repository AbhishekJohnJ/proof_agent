import math
from typing import Dict, Any, Tuple
from backend.models.verification import CheckStatus

class ResultChecker:
    """Verifies that execution output matches expected result types and contains non-null, non-NaN valid values."""

    @classmethod
    def check_result(cls, execution_res: Dict[str, Any], expected_type: str = "number") -> Tuple[CheckStatus, CheckStatus, CheckStatus, list[str]]:
        errors = []

        if not execution_res.get("success", False):
            return CheckStatus.FAIL, CheckStatus.FAIL, CheckStatus.FAIL, [f"Execution failed: {execution_res.get('error', 'unknown error')}"]

        stdout = execution_res.get("stdout", "")
        if not stdout:
            return CheckStatus.PASS, CheckStatus.FAIL, CheckStatus.FAIL, ["Execution completed but produced no stdout output."]

        parsed = execution_res.get("parsed_output")
        if parsed is None:
            return CheckStatus.PASS, CheckStatus.PASS, CheckStatus.FAIL, ["Execution output could not be parsed as valid JSON result."]

        if not isinstance(parsed, dict) or "result" not in parsed:
            return CheckStatus.PASS, CheckStatus.PASS, CheckStatus.FAIL, ["Result object missing 'result' field."]

        val = parsed["result"]

        # Validate based on expected_result_type
        if expected_type in ["number", "integer", "float"]:
            if val is None:
                return CheckStatus.PASS, CheckStatus.PASS, CheckStatus.FAIL, ["Numeric result is null."]
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                return CheckStatus.PASS, CheckStatus.PASS, CheckStatus.FAIL, [f"Expected numeric result but got {type(val).__name__}."]
            if math.isnan(val):
                return CheckStatus.PASS, CheckStatus.PASS, CheckStatus.FAIL, ["Numeric result is NaN."]
            if math.isinf(val):
                return CheckStatus.PASS, CheckStatus.PASS, CheckStatus.FAIL, ["Numeric result is Infinity."]

            return CheckStatus.PASS, CheckStatus.PASS, CheckStatus.PASS, []

        elif expected_type == "table":
            if not isinstance(val, (list, dict)):
                return CheckStatus.PASS, CheckStatus.PASS, CheckStatus.FAIL, ["Expected table output (list/dict) but received primitive."]
            return CheckStatus.PASS, CheckStatus.PASS, CheckStatus.PASS, []

        elif expected_type == "string":
            if val is None or not isinstance(val, str):
                return CheckStatus.PASS, CheckStatus.PASS, CheckStatus.FAIL, ["Expected string result."]
            return CheckStatus.PASS, CheckStatus.PASS, CheckStatus.PASS, []

        elif expected_type == "boolean":
            if not isinstance(val, bool):
                return CheckStatus.PASS, CheckStatus.PASS, CheckStatus.FAIL, ["Expected boolean result."]
            return CheckStatus.PASS, CheckStatus.PASS, CheckStatus.PASS, []

        return CheckStatus.PASS, CheckStatus.PASS, CheckStatus.PASS, []
