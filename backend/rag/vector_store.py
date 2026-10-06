import numpy as np
from typing import List, Tuple, Dict, Any
from backend.models.document import DocumentChunk

class SimpleVectorStore:
    """In-memory cosine similarity vector store for document chunks."""

    def __init__(self):
        self.chunks: List[DocumentChunk] = []
        self.embeddings: List[np.ndarray] = []

    def add_chunks(self, chunks: List[DocumentChunk], embeddings: List[List[float]]):
        for chunk, emb in zip(chunks, embeddings):
            self.chunks.append(chunk)
            vec = np.array(emb, dtype=np.float32)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            self.embeddings.append(vec)

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        if not self.embeddings:
            return []

        q_vec = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        scores = [float(np.dot(q_vec, emb)) for emb in self.embeddings]
        indexed_scores = list(enumerate(scores))
        indexed_scores.sort(key=lambda x: x[1], reverse=True)

        results = []
        for idx, score in indexed_scores[:top_k]:
            results.append((self.chunks[idx], score))
        return results
