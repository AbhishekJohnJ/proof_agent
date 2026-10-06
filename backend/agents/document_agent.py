from typing import List, Tuple
from backend.models.document import DocumentChunk
from backend.rag.retriever import DocumentRetriever

class DocumentAgent:
    """Agent responsible for document evidence retrieval."""

    def __init__(self, retriever: DocumentRetriever):
        self.retriever = retriever

    def retrieve_supporting_chunks(self, question: str, top_k: int = 3) -> List[Tuple[DocumentChunk, float]]:
        return self.retriever.retrieve(question, top_k=top_k)
