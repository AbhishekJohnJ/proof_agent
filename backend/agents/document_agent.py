from typing import List, Tuple, Optional
from backend.models.document import DocumentChunk
from backend.rag.retriever import DocumentRetriever

class DocumentAgent:
    """Agent responsible for scoped document retrieval."""

    def __init__(self, retriever: DocumentRetriever):
        self.retriever = retriever

    def retrieve_supporting_chunks(
        self,
        question: str,
        selected_document_ids: Optional[List[str]] = None,
        top_k: int = 3
    ) -> List[Tuple[DocumentChunk, float]]:
        return self.retriever.retrieve(question, selected_document_ids=selected_document_ids, top_k=top_k)
