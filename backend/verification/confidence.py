from typing import List
from backend.models.verification import VerificationResult, CheckStatus
from backend.models.dataset import QualityWarning

class ConfidenceCalculator:
    """Calculates deterministic confidence scores based on verification signals.
    
    Formula:
    Base Score = 0.6 if Execution == PASS and Output == PASS
    + 0.25 if Reproducibility == PASS
    + 0.15 if Selected Datasets Used == PASS
    - 0.20 if Critical Quality Issues exist
    - 0.05 per Warning Quality Issue
    Score is hard-capped at 0.0 if Execution or Output Verification fails.
    """

    @classmethod
    def calculate_confidence(cls, verification: VerificationResult, warnings: List[QualityWarning]) -> float:
        if verification.execution_success != CheckStatus.PASS or verification.output_valid != CheckStatus.PASS:
            return 0.0

        if verification.status in ["VERIFICATION_FAILED", "REFUSED", "EXECUTION_FAILED"]:
            return 0.0

        score = 0.60  # Base confidence for clean execution and valid output

        if verification.reproducible == CheckStatus.PASS:
            score += 0.25

        if verification.selected_datasets_used == CheckStatus.PASS:
            score += 0.15

        critical_count = sum(1 for w in warnings if w.severity == "critical")
        warning_count = sum(1 for w in warnings if w.severity == "warning")

        score -= (critical_count * 0.20 + warning_count * 0.05)

        return max(0.0, min(1.0, round(score, 2)))
