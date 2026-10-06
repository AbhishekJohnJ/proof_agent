from typing import Optional
from pydantic import BaseModel, Field

class VerificationResult(BaseModel):
    executed: bool = False
    execution_success: bool = False
    output_present: bool = False
    output_valid: bool = False
    reproducible: bool = False
    datasets_used: list[str] = Field(default_factory=list)
    filters_verified: bool = False
    data_quality_checked: bool = False
    answer_matches_output: bool = False
    status: str = "unverified"  # verified | unverified | failed | refused
    confidence_score: float = 0.0
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
