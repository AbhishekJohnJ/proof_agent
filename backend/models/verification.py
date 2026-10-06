from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field

class CheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_CHECKED = "NOT_CHECKED"
    NOT_APPLICABLE = "NOT_APPLICABLE"

class VerificationResult(BaseModel):
    # V1 to V13 Checks
    v1_code_executed: CheckStatus = CheckStatus.NOT_CHECKED
    v2_output_exists: CheckStatus = CheckStatus.NOT_CHECKED
    v3_output_valid_canonical: CheckStatus = CheckStatus.NOT_CHECKED
    v4_result_type_matched: CheckStatus = CheckStatus.NOT_CHECKED
    v5_result_finite_valid: CheckStatus = CheckStatus.NOT_CHECKED
    v6_reproducible: CheckStatus = CheckStatus.NOT_CHECKED
    v7_required_datasets_used: CheckStatus = CheckStatus.NOT_CHECKED
    v8_required_columns_used: CheckStatus = CheckStatus.NOT_CHECKED
    v9_expected_operation_reflected: CheckStatus = CheckStatus.NOT_CHECKED
    v10_final_answer_consistent: CheckStatus = CheckStatus.NOT_CHECKED
    v11_unit_matched: CheckStatus = CheckStatus.NOT_CHECKED
    v12_quality_requirements_satisfied: CheckStatus = CheckStatus.NOT_CHECKED
    v13_evidence_sources_matched: CheckStatus = CheckStatus.NOT_CHECKED

    # Legacy compatibility fields
    executed: CheckStatus = CheckStatus.NOT_CHECKED
    execution_success: CheckStatus = CheckStatus.NOT_CHECKED
    output_present: CheckStatus = CheckStatus.NOT_CHECKED
    output_valid: CheckStatus = CheckStatus.NOT_CHECKED
    expected_type_matched: CheckStatus = CheckStatus.NOT_CHECKED
    reproducible: CheckStatus = CheckStatus.NOT_CHECKED
    selected_datasets_used: CheckStatus = CheckStatus.NOT_CHECKED
    result_consistent: CheckStatus = CheckStatus.NOT_CHECKED

    quality_check_performed: bool = True
    quality_issues_found: bool = False
    critical_quality_issues: bool = False

    status: str = "UNVERIFIED"  # VERIFIED | VERIFICATION_FAILED | REFUSED | UNVERIFIED
    confidence_score: float = 0.0
    comparison_method: str = "exact_match"
    numeric_tolerance_difference: float = 0.0

    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    diagnostic_details: dict[str, Any] = Field(default_factory=dict)
