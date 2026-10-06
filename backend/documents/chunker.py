import uuid
from typing import List, Dict, Any
from backend.models.document import DocumentChunk

class DocumentChunker:
    """Splits extracted page text into structured DocumentChunk objects."""

    @classmethod
    def create_chunks(cls, document_id: str, document_name: str, pages: List[Dict[str, Any]], max_chunk_chars: int = 1000, overlap_chars: int = 150) -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []

        for page in pages:
            page_num = page["page_number"]
            text = page["text"].strip()

            if not text:
                continue

            # If text fits in single chunk
            if len(text) <= max_chunk_chars:
                chunk_id = f"chk_{uuid.uuid4().hex[:8]}"
                chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    document_name=document_name,
                    page_number=page_num,
                    section=None,
                    text=text,
                    metadata={"char_len": len(text)}
                ))
            else:
                # Overlapping window chunker
                start = 0
                while start < len(text):
                    end = min(start + max_chunk_chars, len(text))
                    chunk_text = text[start:end].strip()

                    if chunk_text:
                        chunk_id = f"chk_{uuid.uuid4().hex[:8]}"
                        chunks.append(DocumentChunk(
                            chunk_id=chunk_id,
                            document_id=document_id,
                            document_name=document_name,
                            page_number=page_num,
                            section=None,
                            text=chunk_text,
                            metadata={"char_len": len(chunk_text), "start_char": start, "end_char": end}
                        ))

                    if end == len(text):
                        break
                    start += (max_chunk_chars - overlap_chars)

        return chunks
