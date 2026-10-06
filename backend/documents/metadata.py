import pandas as pd
from pathlib import Path
from backend.models.document import DocumentMetadata

class MetadataExtractor:
    """Extracts document file-level metadata safely."""

    @classmethod
    def extract_metadata(cls, document_id: str, file_path: Path | str, page_count: int, chunk_count: int) -> DocumentMetadata:
        path = Path(file_path)
        stat = path.stat() if path.exists() else None
        size_bytes = stat.st_size if stat else 0

        return DocumentMetadata(
            document_id=document_id,
            filename=path.name,
            file_type=path.suffix.lstrip(".").lower(),
            page_count=page_count,
            chunk_count=chunk_count,
            file_size_bytes=size_bytes,
            created_at=pd.Timestamp.now().isoformat(),
            status="success"
        )
