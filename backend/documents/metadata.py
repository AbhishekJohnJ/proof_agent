import pandas as pd
from pathlib import Path
from backend.models.document import DocumentMetadata

class MetadataExtractor:
    """Extracts document file-level metadata."""

    @classmethod
    def extract_metadata(cls, document_id: str, file_path: Path, page_count: int, chunk_count: int) -> DocumentMetadata:
        stat = file_path.stat()
        return DocumentMetadata(
            document_id=document_id,
            filename=file_path.name,
            file_type=file_path.suffix.lstrip(".").lower(),
            page_count=page_count,
            chunk_count=chunk_count,
            file_size_bytes=stat.st_size,
            created_at=pd.Timestamp.now().isoformat(),
            status="success"
        )
