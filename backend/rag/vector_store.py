import numpy as np
from typing import List, Tuple, Optional
from backend.models.document import DocumentChunk

class SimpleVectorStore:
    """In-memory cosine similarity vector store with strict document ID filtering."""

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

    def search(
        self,
        query_embedding: List[float],
        selected_document_ids: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[Tuple[DocumentChunk, float]]:
        if not self.embeddings:
            return []

        q_vec = np.array(query_embedding, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        scores = [float(np.dot(q_vec, emb)) for emb in self.embeddings]
        
        results = []
        for idx, score in enumerate(scores):
            chunk = self.chunks[idx]

            # Strict document scoping filter
            if selected_document_ids and len(selected_document_ids) > 0:
                if chunk.document_id not in selected_document_ids:
                    continue

            results.append((chunk, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

# Global vector store instance
global_vector_store = SimpleVectorStore()
