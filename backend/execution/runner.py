import sys
import subprocess
import tempfile
import json
from pathlib import Path
from typing import Dict, Any
from backend.execution.limits import ExecutionLimits

class LocalCodeRunner:
    """Executes Python code in an isolated subprocess with timeout and resource limits."""

    @classmethod
    def run_code(cls, code: str, cwd: Path | None = None, limits: ExecutionLimits | None = None) -> Dict[str, Any]:
        limits = limits or ExecutionLimits()

        # Write code to temporary script
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
            tmp.write(code)
            tmp_path = Path(tmp.name)

        try:
            res = subprocess.run(
                [sys.executable, str(tmp_path)],
                cwd=cwd or Path.cwd(),
                capture_output=True,
                text=True,
                timeout=limits.timeout_seconds
            )

            stdout = res.stdout.strip()
            stderr = res.stderr.strip()

            parsed_output = None
            if stdout:
                # Try parsing JSON output from stdout
                try:
                    # Find last line matching JSON if multiple lines
                    for line in reversed(stdout.splitlines()):
                        if line.strip().startswith("{") and line.strip().endswith("}"):
                            parsed_output = json.loads(line.strip())
                            break
                    if parsed_output is None:
                        parsed_output = {"raw_stdout": stdout}
                except Exception:
                    parsed_output = {"raw_stdout": stdout}

            return {
                "success": res.returncode == 0,
                "returncode": res.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "parsed_output": parsed_output,
                "error": None if res.returncode == 0 else f"Process exited with code {res.returncode}: {stderr}"
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "Execution timed out.",
                "parsed_output": None,
                "error": f"Execution timed out after {limits.timeout_seconds} seconds."
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "parsed_output": None,
                "error": f"Execution failed: {str(e)}"
            }
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
