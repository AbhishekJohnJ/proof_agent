import os
import sys
import shutil
import subprocess
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

class OllamaDiscovery:
    """
    Platform-aware automatic discovery utility for local Ollama installation,
    running service status, API connectivity, and installed models.
    """

    DEFAULT_BASE_URL = "http://localhost:11434"

    @classmethod
    def get_base_url(cls) -> str:
        url = os.getenv("OLLAMA_BASE_URL", "").strip()
        if not url:
            url = cls.DEFAULT_BASE_URL
        return url.rstrip("/")

    @classmethod
    def find_executable(cls) -> Optional[str]:
        """Discovers the Ollama binary location across Windows, macOS, and Linux without hardcoding."""
        # 1. Check PATH
        which_path = shutil.which("ollama")
        if which_path:
            return which_path

        # 2. Check platform-specific common paths
        system = sys.platform.lower()
        candidates = []

        if system.startswith("win"):
            local_app_data = os.getenv("LOCALAPPDATA", "")
            if local_app_data:
                candidates.append(os.path.join(local_app_data, "Programs", "Ollama", "ollama.exe"))
            candidates.extend([
                r"C:\Program Files\Ollama\ollama.exe",
                r"C:\Users\Public\Ollama\ollama.exe"
            ])
        elif system.startswith("darwin"):
            candidates.extend([
                "/usr/local/bin/ollama",
                "/opt/homebrew/bin/ollama",
                "/Applications/Ollama.app/Contents/Resources/ollama"
            ])
        else: # linux
            candidates.extend([
                "/usr/local/bin/ollama",
                "/usr/bin/ollama",
                "/bin/ollama",
                "/snap/bin/ollama"
            ])

        for path in candidates:
            if os.path.isfile(path) and os.access(path, os.X_OK if not system.startswith("win") else os.R_OK):
                return path

        return None

    @classmethod
    def check_version(cls, exe_path: Optional[str] = None) -> Optional[str]:
        """Runs `ollama --version` to extract installed version string."""
        exe = exe_path or cls.find_executable() or "ollama"
        try:
            res = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                output = (res.stdout or res.stderr).strip()
                # Parse e.g. "ollama version is 0.40.0" -> "0.40.0"
                if "version is" in output:
                    return output.split("version is")[-1].strip()
                return output
        except Exception:
            pass
        return None

    @classmethod
    def check_api_status(cls, base_url: Optional[str] = None) -> Dict[str, Any]:
        """Checks if Ollama HTTP API service is running and listening."""
        url = (base_url or cls.get_base_url()).rstrip("/")
        tags_url = f"{url}/api/tags"
        try:
            req = urllib.request.Request(tags_url, headers={"User-Agent": "ProofAI-Discovery/1.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    models = data.get("models", [])
                    return {
                        "available": True,
                        "status_code": 200,
                        "base_url": url,
                        "models": models
                    }
        except urllib.error.HTTPError as e:
            return {"available": False, "status_code": e.code, "error": str(e), "base_url": url, "models": []}
        except Exception as e:
            return {"available": False, "status_code": 0, "error": str(e), "base_url": url, "models": []}

        return {"available": False, "status_code": 0, "error": "Connection failed", "base_url": url, "models": []}

    @classmethod
    def list_models_cli(cls, exe_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fallback list models via `ollama list` CLI command."""
        exe = exe_path or cls.find_executable() or "ollama"
        models = []
        try:
            res = subprocess.run([exe, "list"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                lines = res.stdout.strip().splitlines()
                if len(lines) > 1:
                    # Skip header line
                    for line in lines[1:]:
                        parts = line.split()
                        if parts:
                            name = parts[0]
                            size = parts[2] if len(parts) > 2 else ""
                            models.append({"name": name, "model": name, "size": size})
        except Exception:
            pass
        return models

    @classmethod
    def discover_all(cls) -> Dict[str, Any]:
        """
        Executes complete discovery pipeline and returns authoritative platform status,
        Ollama version, executable path, API status, and installed models.
        """
        exe_path = cls.find_executable()
        version = cls.check_version(exe_path)
        api_result = cls.check_api_status()

        models = api_result.get("models", [])
        if not models and exe_path:
            models = cls.list_models_cli(exe_path)

        model_names = [m.get("name", m.get("model", "")) for m in models]

        # Identify Qwen model
        qwen_models = [m for m in model_names if "qwen" in m.lower()]
        deepseek_models = [m for m in model_names if "deepseek" in m.lower()]

        # Selected models (env override first, then discovered)
        env_planner_model = os.getenv("OLLAMA_PLANNER_MODEL", "").strip()
        env_code_model = os.getenv("OLLAMA_CODE_MODEL", "").strip()

        planner_model = env_planner_model if env_planner_model else (qwen_models[0] if qwen_models else (model_names[0] if model_names else None))
        code_model = env_code_model if env_code_model else (deepseek_models[0] if deepseek_models else (model_names[0] if model_names else None))

        return {
            "executable_path": exe_path,
            "version": version,
            "api_url": api_result.get("base_url", cls.get_base_url()),
            "api_available": api_result.get("available", False),
            "installed_models": models,
            "model_names": model_names,
            "qwen_models": qwen_models,
            "deepseek_models": deepseek_models,
            "selected_planner_model": planner_model,
            "selected_code_model": code_model
        }
