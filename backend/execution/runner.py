from pathlib import Path
from typing import Dict, Any, List
from backend.execution.limits import ExecutionLimits
from backend.execution.sandbox import LocalIsolatedSandbox
from backend.models.dataset import DatasetArtifact

class LocalCodeRunner:
    """Wrapper class executing Python code using LocalIsolatedSandbox."""

    @classmethod
    def run_code(cls, code: str, datasets: List[DatasetArtifact] | None = None, limits: ExecutionLimits | None = None) -> Dict[str, Any]:
        sandbox = LocalIsolatedSandbox(limits=limits)
        return sandbox.execute(code, datasets or [])
