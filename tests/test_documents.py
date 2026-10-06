from pathlib import Path
from backend.documents.extractor import DocumentExtractor
from backend.documents.chunker import DocumentChunker

def test_txt_document_extraction():
    path = Path("documents/sample/annual_report.txt")
    pages = DocumentExtractor.extract_pages(path)

    assert len(pages) > 0
    assert pages[0]["page_number"] == 1
    assert "GlobalCorp" in pages[0]["text"]

def test_document_chunker():
    pages = [{"page_number": 1, "text": "This is page 1 content. " * 50}]
    chunks = DocumentChunker.create_chunks("doc_1", "annual_report.txt", pages, max_chunk_chars=200)

    assert len(chunks) > 1
    assert chunks[0].document_id == "doc_1"
    assert chunks[0].page_number == 1
