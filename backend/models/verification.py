from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field

class CheckStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_CHECKED = "NOT_CHECKED"
    NOT_APPLICABLE = "NOT_APPLICABLE"

class VerificationResult(BaseModel):
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
