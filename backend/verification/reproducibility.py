import math
from typing import Dict, Any, Tuple, List
from backend.execution.sandbox import SandboxExecutionEnvironment
from backend.models.dataset import DatasetArtifact
from backend.models.verification import CheckStatus

class ReproducibilityVerifier:
    """Verifies that code execution produces identical or numerically tolerant outputs on repeat runs."""

    @classmethod
    def verify_reproducibility(
        cls,
        sandbox: SandboxExecutionEnvironment,
        code: str,
        initial_res: Dict[str, Any],
        datasets: List[DatasetArtifact],
        tolerance: float = 1e-6
    ) -> Tuple[CheckStatus, float, str, list[str]]:
        errors = []

        run2 = sandbox.execute(code, datasets)
        if not run2.get("success", False):
            return CheckStatus.FAIL, 0.0, "execution_failure", ["Reproducibility test failed: second execution crashed."]

        out1 = initial_res.get("parsed_output")
        out2 = run2.get("parsed_output")

        if out1 is None or out2 is None:
            if initial_res.get("stdout") == run2.get("stdout"):
                return CheckStatus.PASS, 0.0, "exact_stdout_match", []
            else:
                return CheckStatus.FAIL, 0.0, "stdout_mismatch", ["Stdout mismatch on repeat execution."]

        if out1 == out2:
            return CheckStatus.PASS, 0.0, "exact_canonical_match", []

        # Compare numeric results with tolerance
        if isinstance(out1, dict) and isinstance(out2, dict) and "result" in out1 and "result" in out2:
            v1, v2 = out1["result"], out2["result"]
            if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                diff = abs(v1 - v2)
                if diff <= tolerance or math.isclose(v1, v2, rel_tol=1e-5, abs_tol=tolerance):
                    return CheckStatus.PASS, round(diff, 6), "numeric_tolerance", []
                else:
                    return CheckStatus.FAIL, round(diff, 6), "numeric_tolerance", [f"Numeric result mismatch on repeat run: {v1} vs {v2} (diff: {diff})."]

        return CheckStatus.FAIL, 0.0, "canonical_mismatch", [f"Output mismatch on repeat run: {out1} vs {out2}."]
