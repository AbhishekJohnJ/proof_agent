from backend.config import settings
from backend.providers.base import LLMProvider, EmbeddingProvider, CodeGenerationProvider
from backend.providers.mock import MockLLMProvider, MockEmbeddingProvider, MockCodeGenerationProvider
from backend.providers.ollama import OllamaPlanner, OllamaCodeGenerator, OllamaClient, OllamaDiscovery, ollama_config

class UnconfiguredLLMProvider(LLMProvider):
    """Stub LLM provider returned when an external model is requested but not installed."""

    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> str:
        raise NotImplementedError(f"Model provider '{self.model_name}' is not configured on this environment.")

    def plan_query(self, question: str, dataset_schemas: list[dict], document_summaries: list[dict]) -> dict:
        return {
            "query_type": "unanswerable",
            "datasets_required": [],
            "documents_required": [],
            "operations": [],
            "needs_code": False,
            "needs_retrieval": False,
            "is_unanswerable": True,
            "ambiguity_flags": [f"model_not_configured:{self.model_name}"],
            "refusal_reason": f"Model provider '{self.model_name}' is not installed or configured."
        }

class UnconfiguredCodeGenerationProvider(CodeGenerationProvider):
    """Stub CodeGen provider returned when an external code model is requested but not installed."""

    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate_code(self, question: str, dataset_schemas: list[dict], quality_warnings: list[dict], analysis_contract: any = None) -> dict:
        return {
            "code": f"# MODEL NOT CONFIGURED: {self.model_name}\nprint('{{\"result\": null, \"error\": \"Model provider {self.model_name} not configured\"}}')",
            "explanation": f"Model provider {self.model_name} is not installed.",
            "expected_result_type": "refusal",
            "datasets_used": []
        }

class ProviderFactory:
    """Factory resolving configured providers from settings or environment variables."""

    @classmethod
    def get_llm_provider(cls) -> LLMProvider:
        provider_name = settings.LLM_PROVIDER.lower()
        if provider_name in ["ollama", "qwen", "qwen3"]:
            return OllamaPlanner()
        elif provider_name == "mock":
            return MockLLMProvider(model_name=settings.LLM_MODEL)
        else:
            return UnconfiguredLLMProvider(model_name=provider_name)

    @classmethod
    def get_code_gen_provider(cls) -> CodeGenerationProvider:
        provider_name = settings.CODE_GEN_PROVIDER.lower()
        if provider_name in ["ollama", "deepseek", "deepseek-coder"]:
            return OllamaCodeGenerator()
        elif provider_name == "mock":
            return MockCodeGenerationProvider()
        else:
            return UnconfiguredCodeGenerationProvider(model_name=provider_name)

    @classmethod
    def get_embedding_provider(cls) -> EmbeddingProvider:
        provider_name = settings.EMBEDDING_PROVIDER.lower()
        if provider_name == "mock":
            return MockEmbeddingProvider(dimension=128)
        else:
            # Fall back to mock embedding if unconfigured to keep vector operations functional
            return MockEmbeddingProvider(dimension=128)

    @classmethod
    def get_health_status(cls) -> dict:
        """Returns health and status diagnostic report for configured providers."""
        client = OllamaClient()
        hc = client.health_check()
        disc = OllamaDiscovery.discover_all()

        planner_provider = settings.LLM_PROVIDER.lower()
        code_provider = settings.CODE_GEN_PROVIDER.lower()

        planner_model = ollama_config.planner_model if planner_provider in ["ollama", "qwen", "qwen3"] else settings.LLM_MODEL
        code_model = ollama_config.code_model if code_provider in ["ollama", "deepseek", "deepseek-coder"] else settings.CODE_MODEL

        installed_models = hc.get("models", [])

        return {
            "ollama": {
                "available": hc.get("available", False),
                "base_url": hc.get("base_url", "http://localhost:11434"),
                "executable_path": disc.get("executable_path"),
                "version": disc.get("version"),
                "installed_models": installed_models
            },
            "planner": {
                "provider": planner_provider,
                "model": planner_model,
                "available": hc.get("available", False) and (planner_model in installed_models or planner_provider == "mock")
            },
            "code_generator": {
                "provider": code_provider,
                "model": code_model,
                "available": hc.get("available", False) and (code_model in installed_models or code_provider == "mock")
            }
        }

