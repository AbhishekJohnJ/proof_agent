from typing import Dict, Any, Tuple
from pathlib import Path
from backend.execution.sandbox import SandboxExecutionEnvironment

class ReproducibilityVerifier:
    """Verifies that code execution produces identical output on repeat runs."""

    @classmethod
    def verify_reproducibility(cls, sandbox: SandboxExecutionEnvironment, code: str, initial_res: Dict[str, Any], cwd: Path | None = None) -> Tuple[bool, list[str]]:
        errors = []

        # Run code second time
        run2 = sandbox.execute(code, cwd=cwd)

        if not run2.get("success", False):
            return False, ["Reproducibility test failed: second execution crashed."]

        out1 = initial_res.get("parsed_output")
        out2 = run2.get("parsed_output")

        if out1 != out2:
            errors.append(f"Reproducibility test failed: output mismatch ({out1} vs {out2}).")
            return False, errors

        return True, []
