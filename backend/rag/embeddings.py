from typing import List
from backend.providers.base import EmbeddingProvider

class EmbeddingService:
    """Service wrapping EmbeddingProvider for vector operations."""

    def __init__(self, provider: EmbeddingProvider):
        self.provider = provider

    def embed_query(self, query: str) -> List[float]:
        return self.provider.embed_text(query)

    def embed_chunks(self, texts: List[str]) -> List[List[float]]:
        return self.provider.embed_batch(texts)
