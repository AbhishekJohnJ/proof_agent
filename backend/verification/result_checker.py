from typing import Dict, Any, Tuple

class ResultChecker:
    """Verifies that code execution produced valid non-null numerical/tabular output."""

    @classmethod
    def check_result(cls, execution_res: Dict[str, Any], expected_type: str = "number") -> Tuple[bool, bool, list[str]]:
        errors = []

        if not execution_res.get("success", False):
            return False, False, [f"Execution failed: {execution_res.get('error', 'unknown error')}"]

        stdout = execution_res.get("stdout", "")
        if not stdout:
            return True, False, ["Execution completed but produced no output on stdout."]

        parsed = execution_res.get("parsed_output")
        if parsed is None:
            return True, False, ["Execution output could not be parsed as valid result object."]

        # Check result field
        if isinstance(parsed, dict) and "result" in parsed:
            val = parsed["result"]
            if val is None:
                return True, False, ["Execution produced null result."]
            if expected_type == "number" and not isinstance(val, (int, float)):
                errors.append(f"Expected numeric result but got {type(val).__name__}.")
                return True, False, errors
            return True, True, []

        return True, True, []
