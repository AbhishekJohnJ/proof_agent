from typing import List, Dict, Any
from backend.models.evidence import EvidenceItem, EvidenceType, EvidenceCollection

class EvidenceAccumulator:
    """Accumulates evidence items from data profiling, document retrieval, code, and execution."""

    @classmethod
    def build_evidence(cls, datasets: List[str], code: str, execution_res: Dict[str, Any], doc_chunks: List[Any] | None = None) -> EvidenceCollection:
        items: List[EvidenceItem] = []

        # Data evidence
        for ds in datasets:
            items.append(EvidenceItem(
                type=EvidenceType.DATA,
                source=ds,
                description=f"Tabular dataset '{ds}' used in analytical query.",
                dataset_id=ds
            ))

        # Code evidence
        if code:
            items.append(EvidenceItem(
                type=EvidenceType.CODE,
                source="generated_script.py",
                description="Self-contained Python executable script.",
                details={"code": code}
            ))

        # Execution evidence
        if execution_res:
            items.append(EvidenceItem(
                type=EvidenceType.EXECUTION,
                source="python_sandbox",
                description="Deterministic sandbox execution output.",
                details={"stdout": execution_res.get("stdout"), "parsed": execution_res.get("parsed_output")}
            ))

        # Document evidence
        if doc_chunks:
            for chunk in doc_chunks:
                chunk_obj = chunk[0] if isinstance(chunk, tuple) else chunk
                items.append(EvidenceItem(
                    type=EvidenceType.DOCUMENT,
                    source=getattr(chunk_obj, "document_name", "document"),
                    description=f"Supporting excerpt from page {getattr(chunk_obj, 'page_number', 1)}.",
                    page_number=getattr(chunk_obj, "page_number", 1),
                    chunk_id=getattr(chunk_obj, "chunk_id", None),
                    details={"text": getattr(chunk_obj, "text", "")}
                ))

        return EvidenceCollection(items=items)
