import sys
import json
import shutil
import tempfile
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.execution.limits import ExecutionLimits
from backend.models.dataset import DatasetArtifact

class SandboxExecutionEnvironment(ABC):
    """Abstract sandbox environment interface."""

    @abstractmethod
    def execute(self, code: str, datasets: Optional[List[DatasetArtifact]] = None) -> Dict[str, Any]:
        raise NotImplementedError

class LocalIsolatedSandbox(SandboxExecutionEnvironment):
    """Development process sandbox using isolated workspace directory and process boundaries."""

    def __init__(self, limits: ExecutionLimits | None = None):
        self.limits = limits or ExecutionLimits()

    def execute(self, code: str, datasets: Optional[List[DatasetArtifact]] = None) -> Dict[str, Any]:
        datasets = datasets or []
        with tempfile.TemporaryDirectory(prefix="proofai_sandbox_") as tmpdir:
            tmp_path = Path(tmpdir)
            data_dir = tmp_path / "data"
            data_dir.mkdir(parents=True, exist_ok=True)

            for artifact in datasets:
                ds_dir = data_dir / artifact.dataset_id
                ds_dir.mkdir(parents=True, exist_ok=True)
                src_file = Path(artifact.workspace_path)
                if src_file.exists():
                    shutil.copy2(src_file, ds_dir / f"data{src_file.suffix.lower()}")

            script_path = tmp_path / "script.py"
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code)

            try:
                res = subprocess.run(
                    [sys.executable, str(script_path)],
                    cwd=tmp_path,
                    capture_output=True,
                    text=True,
                    timeout=self.limits.timeout_seconds
                )

                stdout = res.stdout[:self.limits.max_output_bytes].strip()
                stderr = res.stderr[:self.limits.max_output_bytes].strip()

                parsed_output = None
                if stdout:
                    try:
                        for line in reversed(stdout.splitlines()):
                            line_str = line.strip()
                            if line_str.startswith("{") and line_str.endswith("}"):
                                parsed_output = json.loads(line_str)
                                break
                    except Exception:
                        parsed_output = None

                return {
                    "success": res.returncode == 0,
                    "returncode": res.returncode,
                    "stdout": stdout,
                    "stderr": stderr,
                    "parsed_output": parsed_output,
                    "execution_mode": "local_isolated",
                    "error": None if res.returncode == 0 else f"Process exited with code {res.returncode}: {stderr}"
                }
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "returncode": -1,
                    "stdout": "",
                    "stderr": f"Execution timed out after {self.limits.timeout_seconds} seconds.",
                    "parsed_output": None,
                    "execution_mode": "local_isolated",
                    "error": f"Execution timed out after {self.limits.timeout_seconds} seconds."
                }
            except Exception as e:
                return {
                    "success": False,
                    "returncode": -1,
                    "stdout": "",
                    "stderr": str(e),
                    "parsed_output": None,
                    "execution_mode": "local_isolated",
                    "error": f"Execution failed: {str(e)}"
                }

class DockerSandbox(SandboxExecutionEnvironment):
    """Production hardened Docker sandbox environment. NO SILENT FALLBACK to host execution when unavailable."""

    def __init__(self, limits: ExecutionLimits | None = None, docker_image: str = "proofai-sandbox:latest"):
        self.limits = limits or ExecutionLimits()
        self.docker_image = docker_image

    def execute(self, code: str, datasets: Optional[List[DatasetArtifact]] = None) -> Dict[str, Any]:
        datasets = datasets or []
        with tempfile.TemporaryDirectory(prefix="proofai_docker_ws_") as tmpdir:
            tmp_path = Path(tmpdir)
            data_dir = tmp_path / "data"
            data_dir.mkdir(parents=True, exist_ok=True)

            for artifact in datasets:
                ds_dir = data_dir / artifact.dataset_id
                ds_dir.mkdir(parents=True, exist_ok=True)
                src_file = Path(artifact.workspace_path)
                if src_file.exists():
                    shutil.copy2(src_file, ds_dir / f"data{src_file.suffix.lower()}")

            script_path = tmp_path / "script.py"
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code)

            cmd = [
                "docker", "run", "--rm",
                "--network", "none",
                "--memory", f"{self.limits.max_memory_mb}m",
                "--cpus", "1.0",
                "-v", f"{tmp_path.resolve()}:/workspace:ro",
                "-w", "/workspace",
                self.docker_image,
                "python3", "/workspace/script.py"
            ]

            try:
                res = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.limits.timeout_seconds
                )
                stdout = res.stdout[:self.limits.max_output_bytes].strip()
                stderr = res.stderr[:self.limits.max_output_bytes].strip()

                parsed_output = None
                if stdout:
                    for line in reversed(stdout.splitlines()):
                        line_str = line.strip()
                        if line_str.startswith("{") and line_str.endswith("}"):
                            try:
                                parsed_output = json.loads(line_str)
                                break
                            except Exception:
                                pass

                return {
                    "success": res.returncode == 0,
                    "returncode": res.returncode,
                    "stdout": stdout,
                    "stderr": stderr,
                    "parsed_output": parsed_output,
                    "execution_mode": "docker_sandbox",
                    "error": None if res.returncode == 0 else stderr
                }
            except Exception as e:
                # Docker is unavailable - NO SILENT FALLBACK to host!
                return {
                    "success": False,
                    "returncode": -1,
                    "stdout": "",
                    "stderr": f"Docker sandbox unavailable: {str(e)}",
                    "parsed_output": None,
                    "execution_mode": "docker_unavailable",
                    "error": "sandbox_unavailable"
                }
