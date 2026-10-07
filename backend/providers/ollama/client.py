import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from backend.providers.ollama.config import ollama_config
from backend.providers.ollama.exceptions import (
    OllamaProviderError,
    OllamaUnavailableError,
    ModelNotFoundError,
    OllamaTimeoutError,
    OllamaResponseError
)

class OllamaClient:
    """
    Reusable HTTP Client for interacting with the local Ollama REST API.
    Supports generation, chat, health checks, model verification, and model listing.
    """

    def __init__(self, base_url: Optional[str] = None, timeout: Optional[int] = None):
        self.base_url = (base_url or ollama_config.base_url).rstrip("/")
        self.timeout = timeout or ollama_config.timeout

    def health_check(self) -> Dict[str, Any]:
        """Checks if local Ollama API is available and returns installed model metadata."""
        url = f"{self.base_url}/api/tags"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ProofAI-Client/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    models = [m.get("name", m.get("model")) for m in data.get("models", [])]
                    return {
                        "available": True,
                        "base_url": self.base_url,
                        "models": models,
                        "raw_models": data.get("models", [])
                    }
        except Exception as e:
            return {
                "available": False,
                "base_url": self.base_url,
                "error": str(e),
                "models": []
            }
        return {"available": False, "base_url": self.base_url, "error": "Unknown connection failure", "models": []}

    def list_models(self) -> List[str]:
        hc = self.health_check()
        if not hc.get("available"):
            raise OllamaUnavailableError(f"Ollama API service unavailable at {self.base_url}: {hc.get('error')}")
        return hc.get("models", [])

    def generate(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_format: bool = False,
        temperature: Optional[float] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calls /api/generate endpoint on local Ollama API.
        Returns dictionary containing 'response', 'total_duration', 'eval_count', etc.
        """
        url = f"{self.base_url}/api/generate"

        opts = options or {}
        if temperature is not None:
            opts["temperature"] = temperature
        else:
            opts["temperature"] = ollama_config.temperature

        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": opts
        }

        if system_prompt:
            payload["system"] = system_prompt

        if json_format:
            payload["format"] = "json"

        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "ProofAI-Client/1.0"
            }
        )

        start_time = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    latency_ms = int((time.perf_counter() - start_time) * 1000)
                    data["latency_ms"] = latency_ms
                    return data
                else:
                    raise OllamaResponseError(f"Ollama API error (HTTP {resp.status})")
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8") if e.fp else str(e)
            if e.code == 404:
                raise ModelNotFoundError(f"Model '{model}' not found in Ollama: {err_msg}")
            raise OllamaResponseError(f"Ollama API HTTP {e.code}: {err_msg}")
        except urllib.error.URLError as e:
            if "timed out" in str(e).lower():
                raise OllamaTimeoutError(f"Ollama request to model '{model}' timed out after {self.timeout}s")
            raise OllamaUnavailableError(f"Failed to connect to local Ollama API at {self.base_url}: {e.reason}")
        except Exception as e:
            raise OllamaProviderError(f"Unexpected error communicating with Ollama: {str(e)}")

    def verify_model_inference(self, model: str) -> Dict[str, Any]:
        """
        Independently verifies that the specified model is installed and capable
        of generating valid inference output on local Ollama API.
        """
        test_prompt = 'Return JSON: {"status": "ok", "model": "' + model + '"}'
        res = self.generate(
            model=model,
            prompt=test_prompt,
            json_format=True,
            temperature=0.0
        )
        response_text = res.get("response", "").strip()
        try:
            import re
            if "```" in response_text:
                match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response_text, re.DOTALL)
                if match:
                    response_text = match.group(1)
                else:
                    response_text = re.sub(r"```(?:json)?|```", "", response_text).strip()
            first = response_text.find("{")
            last = response_text.rfind("}")
            if first != -1 and last != -1 and last >= first:
                response_text = response_text[first:last+1]
            parsed = json.loads(response_text)
            return {
                "verified": True,
                "model": model,
                "latency_ms": res.get("latency_ms", 0),
                "parsed_response": parsed
            }
        except Exception as e:
            return {
                "verified": False,
                "model": model,
                "error": f"Failed to parse JSON test output: {str(e)}",
                "raw_response": response_text
            }
