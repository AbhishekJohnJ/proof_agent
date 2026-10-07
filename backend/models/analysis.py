from enum import Enum
from typing import Any, Optional, List, Dict
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
    MODEL_PREDICTION = "MODEL_PREDICTION"

class CanonicalResult(BaseModel):
    result: Any
    result_type: str = "scalar"  # scalar | ranked_item | grouped_table | percentage | comparison | model_prediction
    metric: str = "result"
    label: Optional[str] = None
    unit: Optional[str] = None
    dataset_ids: List[str] = Field(default_factory=list)
    extra_details: Dict[str, Any] = Field(default_factory=dict)

class AnalysisPlan(BaseModel):
    query_type: str  # data_aggregation | comparison | document_retrieval | hybrid | unanswerable
    datasets_required: List[str] = Field(default_factory=list)
    documents_required: List[str] = Field(default_factory=list)
    columns_required: List[str] = Field(default_factory=list)
    operations: List[Dict[str, Any]] = Field(default_factory=list)
    joins: List[Dict[str, Any]] = Field(default_factory=list)
    filters: List[Dict[str, Any]] = Field(default_factory=list)
    aggregations: List[Dict[str, Any]] = Field(default_factory=list)
    group_by: List[str] = Field(default_factory=list)
    sorting: List[Dict[str, Any]] = Field(default_factory=list)
    needs_code: bool = True
    needs_retrieval: bool = False
    is_unanswerable: bool = False
    ambiguity_flags: List[str] = Field(default_factory=list)
    refusal_reason: Optional[str] = None
    expected_metric: Optional[str] = None
    expected_unit: Optional[str] = None
    return_definition: Optional[str] = None

class AnalysisResult(BaseModel):
    analysis_id: str
    question: str
    answer: str
    status: AnalysisStatus
    result_kind: str = "verified_analysis"  # verified_analysis | model_prediction | refusal | verification_failed
    resolved_dataset_ids: List[str] = Field(default_factory=list)
    analysis_contract: Optional[AnalysisContract] = None
    code: Optional[str] = None
    expected_result_type: str = "number"  # number | integer | float | table | string | boolean | refusal | ranked_item
    execution_result: Optional[Dict[str, Any]] = None
    canonical_result: Optional[CanonicalResult] = None
    reference_result: Optional[Dict[str, Any]] = None
    proof_trace: Optional[Dict[str, Any]] = None
    join_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    accessed_dataset_ids: List[str] = Field(default_factory=list)
    accessed_columns: List[str] = Field(default_factory=list)
    evidence: List[EvidenceItem] = Field(default_factory=list)
    verification: Optional[VerificationResult] = None
    confidence: float = 0.0
    refusal_reason: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None
    attempts_count: int = 1

