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

            # Copy selected datasets into sandbox
            selected_ids = set()
            for artifact in datasets:
                ds_dir = data_dir / artifact.dataset_id
                ds_dir.mkdir(parents=True, exist_ok=True)
                src_file = Path(artifact.workspace_path)
                if src_file.exists():
                    shutil.copy2(src_file, ds_dir / f"data{src_file.suffix.lower()}")
                    # Copy to filename.csv as well for compatibility
                    shutil.copy2(src_file, ds_dir / src_file.name)
                    selected_ids.add(artifact.dataset_id)

            # Also expose other workspace datasets so access to unselected datasets can be detected!
            from backend.services.storage import storage_service
            for ds_id, art in storage_service.dataset_artifacts.items():
                if ds_id not in selected_ids:
                    unsel_dir = data_dir / ds_id
                    unsel_dir.mkdir(parents=True, exist_ok=True)
                    src_f = Path(art.workspace_path)
                    if src_f.exists():
                        shutil.copy2(src_f, unsel_dir / f"data{src_f.suffix.lower()}")
                        shutil.copy2(src_f, unsel_dir / src_f.name)

            # Inject dataset access auditing header
            audit_header = """import builtins, json, os, atexit
_proofai_accessed = set()
_orig_open = builtins.open
def _audit_open(file, *args, **kwargs):
    fstr = str(file)
    if "data/" in fstr or os.path.exists(fstr):
        _proofai_accessed.add(fstr)
    return _orig_open(file, *args, **kwargs)
builtins.open = _audit_open
def _report_access():
    print("__PROOFAI_ACCESSED__:" + json.dumps(list(_proofai_accessed)))
atexit.register(_report_access)
"""
            full_script_code = audit_header + "\n" + code

            script_path = tmp_path / "script.py"
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(full_script_code)

            try:
                res = subprocess.run(
                    [sys.executable, str(script_path)],
                    cwd=tmp_path,
                    capture_output=True,
                    text=True,
                    timeout=self.limits.timeout_seconds
                )

                raw_stdout = res.stdout[:self.limits.max_output_bytes].strip()
                stderr = res.stderr[:self.limits.max_output_bytes].strip()

                # Extract accessed files from stdout
                accessed_files = []
                accessed_dataset_ids = []
                clean_stdout_lines = []

                for line in raw_stdout.splitlines():
                    if line.startswith("__PROOFAI_ACCESSED__:"):
                        try:
                            accessed_files = json.loads(line.replace("__PROOFAI_ACCESSED__:", ""))
                        except Exception:
                            pass
                    else:
                        clean_stdout_lines.append(line)

                stdout = "\n".join(clean_stdout_lines).strip()

                # Extract dataset IDs from accessed file paths
                for fpath in accessed_files:
                    parts = Path(fpath).parts
                    if "data" in parts:
                        idx = parts.index("data")
                        if idx + 1 < len(parts):
                            ds_id = parts[idx + 1]
                            if ds_id and ds_id not in accessed_dataset_ids and ds_id != "script.py":
                                accessed_dataset_ids.append(ds_id)

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
                    "accessed_files": accessed_files,
                    "accessed_dataset_ids": accessed_dataset_ids,
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
                    "accessed_files": [],
                    "accessed_dataset_ids": [],
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
                    "accessed_files": [],
                    "accessed_dataset_ids": [],
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
