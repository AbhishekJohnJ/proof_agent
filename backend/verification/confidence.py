from typing import List
from backend.models.verification import VerificationResult, CheckStatus
from backend.models.dataset import QualityWarning

class ConfidenceCalculator:
    """Calculates deterministic confidence scores based on V1 to V13 verification signals.
    
    Formula:
    Base Score = 0.50 if V1, V2, V3, V4, V5 pass
    + 0.20 if V6 (Reproducibility) passes
    + 0.15 if V7 (Dataset usage) and V10 (Answer consistency) pass
    + 0.15 if V13 (Evidence sources) passes
    - 0.25 if Critical Quality Issues exist
    - 0.05 per Warning Quality Issue
    Score is hard-capped at 0.0 if any core check (V1, V2, V3, V4, V5, V6, V10) fails.
    """

    @classmethod
    def calculate_confidence(cls, verification: VerificationResult, warnings: List[QualityWarning]) -> float:
        core_checks = [
            verification.v1_code_executed,
            verification.v2_output_exists,
            verification.v3_output_valid_canonical,
            verification.v4_result_type_matched,
            verification.v5_result_finite_valid,
            verification.v6_reproducible,
            verification.v10_final_answer_consistent
        ]

        if any(c == CheckStatus.FAIL for c in core_checks):
            return 0.0

        if verification.status in ["VERIFICATION_FAILED", "REFUSED", "EXECUTION_FAILED", "UNVERIFIED"]:
            return 0.0

        score = 0.50  # Base confidence for core execution and validation

        if verification.v6_reproducible == CheckStatus.PASS:
            score += 0.20

        if verification.v7_required_datasets_used == CheckStatus.PASS and verification.v10_final_answer_consistent == CheckStatus.PASS:
            score += 0.15

        if verification.v13_evidence_sources_matched == CheckStatus.PASS:
            score += 0.15

        critical_count = sum(1 for w in warnings if w.severity == "critical")
        warning_count = sum(1 for w in warnings if w.severity == "warning")

        score -= (critical_count * 0.25 + warning_count * 0.05)

        return max(0.0, min(1.0, round(score, 2)))
