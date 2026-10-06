from typing import List, Dict, Any, Tuple
from backend.models.evidence import EvidenceItem, EvidenceType, EvidenceCollection

class EvidenceAccumulator:
    """Accumulates evidence items from data profiling, document retrieval, code, execution, and verification."""

    @classmethod
    def build_evidence(
        cls,
        datasets: List[str],
        code: str,
        execution_res: Dict[str, Any],
        doc_chunks: List[Tuple[Any, float]] | None = None
    ) -> EvidenceCollection:
        items: List[EvidenceItem] = []

        # 1. Data evidence
        for ds in datasets:
            items.append(EvidenceItem(
                type=EvidenceType.DATA,
                source=ds,
                description=f"Tabular dataset artifact '{ds}' used in analytical query.",
                dataset_id=ds
            ))

        # 2. Code evidence
        if code:
            items.append(EvidenceItem(
                type=EvidenceType.CODE,
                source="generated_script.py",
                description="Self-contained, statically validated Python analytical code.",
                details={"code": code}
            ))

        # 3. Execution evidence
        if execution_res:
            items.append(EvidenceItem(
                type=EvidenceType.EXECUTION,
                source=execution_res.get("execution_mode", "sandbox"),
                description="Deterministic sandbox execution stdout & canonical output.",
                details={
                    "stdout": execution_res.get("stdout"),
                    "parsed": execution_res.get("parsed_output"),
                    "execution_mode": execution_res.get("execution_mode")
                }
            ))

        # 4. Document evidence
        if doc_chunks:
            for chunk_tuple in doc_chunks:
                chunk_obj = chunk_tuple[0] if isinstance(chunk_tuple, tuple) else chunk_tuple
                score = chunk_tuple[1] if isinstance(chunk_tuple, tuple) else 1.0

                items.append(EvidenceItem(
                    type=EvidenceType.DOCUMENT,
                    source=getattr(chunk_obj, "document_name", "document"),
                    description=f"Retrieved passage from page {getattr(chunk_obj, 'page_number', 1)} (Relevance score: {score:.2f}).",
                    page_number=getattr(chunk_obj, "page_number", 1),
                    chunk_id=getattr(chunk_obj, "chunk_id", None),
                    details={
                        "document_id": getattr(chunk_obj, "document_id", None),
                        "text": getattr(chunk_obj, "text", ""),
                        "retrieval_score": score
                    }
                ))

        return EvidenceCollection(items=items)
