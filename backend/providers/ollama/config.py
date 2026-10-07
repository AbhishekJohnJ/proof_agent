import os
from typing import Optional
from backend.providers.ollama.discovery import OllamaDiscovery

class OllamaConfig:
    """Configuration holder for local Ollama provider."""

    def __init__(self):
        self._discovery = None

    @property
    def discovery(self):
        if self._discovery is None:
            self._discovery = OllamaDiscovery.discover_all()
        return self._discovery

    def refresh_discovery(self):
        self._discovery = OllamaDiscovery.discover_all()
        return self._discovery

    @property
    def base_url(self) -> str:
        env_url = os.getenv("OLLAMA_BASE_URL", "").strip()
        if env_url:
            return env_url.rstrip("/")
        return self.discovery.get("api_url", "http://localhost:11434")

    @property
    def planner_model(self) -> str:
        env_model = os.getenv("OLLAMA_PLANNER_MODEL", "").strip()
        if env_model:
            return env_model
        disc_model = self.discovery.get("selected_planner_model")
        if disc_model:
            return disc_model
        return "qwen3:8b"

    @property
    def code_model(self) -> str:
        env_model = os.getenv("OLLAMA_CODE_MODEL", "").strip()
        if env_model:
            return env_model
        disc_model = self.discovery.get("selected_code_model")
        if disc_model:
            return disc_model
        return "deepseek-coder-v2:16b-lite-instruct-q4_K_M"

    @property
    def timeout(self) -> int:
        try:
            return int(os.getenv("OLLAMA_TIMEOUT", "180"))
        except ValueError:
            return 180

    @property
    def temperature(self) -> float:
        try:
            return float(os.getenv("OLLAMA_TEMPERATURE", "0.0"))
        except ValueError:
            return 0.0

    @property
    def max_retries(self) -> int:
        try:
            return int(os.getenv("MAX_LLM_RETRIES", "2"))
        except ValueError:
            return 2

    @property
    def debug(self) -> bool:
        return os.getenv("PROOFAI_DEBUG", "false").lower() in ("true", "1", "yes")

ollama_config = OllamaConfig()
