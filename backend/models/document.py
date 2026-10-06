from typing import Any, Optional
from pydantic import BaseModel, Field

class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    page_number: int
    section: Optional[str] = None
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)

class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    file_type: str
    page_count: int
    chunk_count: int
    file_size_bytes: int
    created_at: str
    status: str = "success"
    error_message: Optional[str] = None
