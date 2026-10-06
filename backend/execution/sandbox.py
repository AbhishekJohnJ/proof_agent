from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any
from backend.execution.runner import LocalCodeRunner
from backend.execution.limits import ExecutionLimits

class SandboxExecutionEnvironment(ABC):
    """Abstract sandbox environment interface."""

    @abstractmethod
    def execute(self, code: str, cwd: Path | None = None) -> Dict[str, Any]:
        raise NotImplementedError

class LocalIsolatedSandbox(SandboxExecutionEnvironment):
    """Local isolated process sandbox."""

    def __init__(self, limits: ExecutionLimits | None = None):
        self.limits = limits or ExecutionLimits()

    def execute(self, code: str, cwd: Path | None = None) -> Dict[str, Any]:
        return LocalCodeRunner.run_code(code, cwd=cwd, limits=self.limits)
