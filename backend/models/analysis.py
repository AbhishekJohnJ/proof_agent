from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field
from backend.models.evidence import EvidenceItem
from backend.models.verification import VerificationResult
from backend.models.analysis_contract import AnalysisContract

class AnalysisStatus(str, Enum):
    RECEIVED = "RECEIVED"
    PLANNED = "PLANNED"
    CODE_GENERATED = "CODE_GENERATED"
    CODE_VALIDATED = "CODE_VALIDATED"
    EXECUTING = "EXECUTING"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    VERIFYING = "VERIFYING"
    VERIFIED = "VERIFIED"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"
    REFUSED = "REFUSED"
    MODEL_NOT_CONFIGURED = "MODEL_NOT_CONFIGURED"

class CanonicalResult(BaseModel):
    result: Any
    metric: str
    unit: Optional[str] = None
    dataset_ids: list[str] = Field(default_factory=list)

class AnalysisPlan(BaseModel):
    query_type: str  # data_aggregation | comparison | document_retrieval | hybrid | unanswerable
    datasets_required: list[str] = Field(default_factory=list)
    documents_required: list[str] = Field(default_factory=list)
    columns_required: list[str] = Field(default_factory=list)
    operations: list[dict[str, Any]] = Field(default_factory=list)
    needs_code: bool = True
    needs_retrieval: bool = False
    is_unanswerable: bool = False
    ambiguity_flags: list[str] = Field(default_factory=list)
    refusal_reason: Optional[str] = None

class AnalysisResult(BaseModel):
    analysis_id: str
    question: str
    answer: str
    status: AnalysisStatus
    analysis_contract: Optional[AnalysisContract] = None
    code: Optional[str] = None
    expected_result_type: str = "number"  # number | integer | float | table | string | boolean | refusal
    execution_result: Optional[dict[str, Any]] = None
    canonical_result: Optional[CanonicalResult] = None
    evidence: list[EvidenceItem] = Field(default_factory=list)
    verification: Optional[VerificationResult] = None
    confidence: float = 0.0
    refusal_reason: Optional[str] = None
    warnings: list[str] = Field(default_factory=list)
    error_message: Optional[str] = None
    attempts_count: int = 1
