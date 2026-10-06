import hashlib
from typing import List
from backend.providers.base import EmbeddingProvider

class MockEmbeddingProvider(EmbeddingProvider):
    """Mock Embedding Provider generating deterministic pseudo-embeddings for testing."""

    def __init__(self, dimension: int = 128):
        self.dimension = dimension

    def embed_text(self, text: str) -> List[float]:
        # Generate deterministic vector based on text hash
        hash_digest = hashlib.sha256(text.encode("utf-8")).digest()
        vec = [float((b / 255.0) * 2.0 - 1.0) for b in hash_digest]
        # Tile or slice to dimension
        while len(vec) < self.dimension:
            vec.extend(vec)
        return vec[:self.dimension]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]
