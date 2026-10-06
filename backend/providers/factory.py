from backend.config import settings
from backend.providers.base import LLMProvider, EmbeddingProvider, CodeGenerationProvider
from backend.providers.mock import MockLLMProvider, MockEmbeddingProvider, MockCodeGenerationProvider

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
            "refusal_reason": f"Model provider '{self.model_name}' is pending GPU installation."
        }

class UnconfiguredCodeGenerationProvider(CodeGenerationProvider):
    """Stub CodeGen provider returned when an external code model is requested but not installed."""

    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate_code(self, question: str, dataset_schemas: list[dict], quality_warnings: list[dict]) -> dict:
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
        if provider_name == "mock":
            return MockLLMProvider(model_name=settings.LLM_MODEL)
        else:
            return UnconfiguredLLMProvider(model_name=provider_name)

    @classmethod
    def get_code_gen_provider(cls) -> CodeGenerationProvider:
        provider_name = settings.CODE_GEN_PROVIDER.lower()
        if provider_name == "mock":
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
