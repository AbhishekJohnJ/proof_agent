from typing import List, Tuple
from backend.models.document import DocumentChunk
from backend.rag.vector_store import SimpleVectorStore
from backend.rag.embeddings import EmbeddingService

class DocumentRetriever:
    """Document Chunk Retriever for RAG pipeline."""

    def __init__(self, vector_store: SimpleVectorStore, embedding_service: EmbeddingService):
        self.vector_store = vector_store
        self.embedding_service = embedding_service

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        query_emb = self.embedding_service.embed_query(query)
        return self.vector_store.search(query_emb, top_k=top_k)
