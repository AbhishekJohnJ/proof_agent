from abc import ABC, abstractmethod
from typing import Any, Dict, List

class LLMProvider(ABC):
    """Abstract Base Class for LLM reasoning providers (e.g. Qwen3, MockLLM)."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> str:
        raise NotImplementedError

    @abstractmethod
    def plan_query(self, question: str, dataset_schemas: List[Dict[str, Any]], document_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        raise NotImplementedError

class EmbeddingProvider(ABC):
    """Abstract Base Class for embedding providers (e.g. Qwen3-Embedding, BAAI/bge-m3, MockEmbedding)."""

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        raise NotImplementedError

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

class CodeGenerationProvider(ABC):
    """Abstract Base Class for Code Generation providers (e.g. DeepSeek-Coder, MockCodeGenerator)."""

    @abstractmethod
    def generate_code(self, question: str, dataset_schemas: List[Dict[str, Any]], quality_warnings: List[Dict[str, Any]]) -> Dict[str, Any]:
        raise NotImplementedError

class AgentProvider(ABC):
    """Abstract Base Class for agent orchestration providers."""

    @abstractmethod
    def run_agent(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
