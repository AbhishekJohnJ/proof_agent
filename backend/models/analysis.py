from typing import Any, Optional
from pydantic import BaseModel, Field
from backend.models.evidence import EvidenceItem
from backend.models.verification import VerificationResult

class AnalysisPlan(BaseModel):
    query_type: str  # data_aggregation | comparison | document_retrieval | hybrid | unanswerable
    datasets_required: list[str] = Field(default_factory=list)
    documents_required: list[str] = Field(default_factory=list)
    operations: list[str] = Field(default_factory=list)
    needs_code: bool = True
    needs_retrieval: bool = False
    is_unanswerable: bool = False
    ambiguity_flags: list[str] = Field(default_factory=list)
    refusal_reason: Optional[str] = None

class AnalysisResult(BaseModel):
    analysis_id: str
    question: str
    answer: str
    status: str  # success | refused | error | model_not_configured
    code: Optional[str] = None
    expected_result_type: str = "number"  # number | table | string | refusal
    execution_result: Optional[dict[str, Any]] = None
    evidence: list[EvidenceItem] = Field(default_factory=list)
    verification: Optional[VerificationResult] = None
    confidence: float = 0.0
    refusal_reason: Optional[str] = None
    warnings: list[str] = Field(default_factory=list)
