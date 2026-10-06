from pathlib import Path
from typing import List, Dict, Any

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

class DocumentExtractor:
    """Extracts text preserving page numbers and page-level metadata from PDF, TXT, DOCX."""

    @classmethod
    def extract_pages(cls, file_path: Path) -> List[Dict[str, Any]]:
        ext = file_path.suffix.lower()
        if ext == ".txt":
            return cls._extract_txt(file_path)
        elif ext == ".pdf":
            return cls._extract_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return cls._extract_docx(file_path)
        else:
            raise ValueError(f"Unsupported document format '{ext}'. Supported: .pdf, .txt, .docx")

    @classmethod
    def _extract_txt(cls, file_path: Path) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        return [{"page_number": 1, "text": text}]

    @classmethod
    def _extract_pdf(cls, file_path: Path) -> List[Dict[str, Any]]:
        if not PYMUPDF_AVAILABLE:
            raise RuntimeError("PyMuPDF is not installed. PDF extraction requires PyMuPDF.")
        
        pages = []
        doc = fitz.open(file_path)
        for i, page in enumerate(doc):
            text = page.get_text()
            pages.append({
                "page_number": i + 1,
                "text": text
            })
        doc.close()
        return pages

    @classmethod
    def _extract_docx(cls, file_path: Path) -> List[Dict[str, Any]]:
        # Fallback TXT style extraction for docx if python-docx not installed
        try:
            import docx
            doc = docx.Document(file_path)
            full_text = "\n".join([p.text for p in doc.paragraphs])
            return [{"page_number": 1, "text": full_text}]
        except ImportError:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            return [{"page_number": 1, "text": text}]
