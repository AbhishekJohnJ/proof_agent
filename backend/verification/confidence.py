from typing import List
from backend.models.verification import VerificationResult
from backend.models.dataset import QualityWarning

class ConfidenceCalculator:
    """Calculates deterministic confidence scores based on verification steps & quality warnings."""

    @classmethod
    def calculate_confidence(cls, verification: VerificationResult, warnings: List[QualityWarning]) -> float:
        if not verification.executed or not verification.execution_success:
            return 0.0

        if not verification.output_present or not verification.output_valid:
            return 0.0

        score = 0.6  # Base score for clean execution

        if verification.reproducible:
            score += 0.25

        if verification.filters_verified:
            score += 0.1

        # Penalize for critical quality warnings
        critical_count = sum(1 for w in warnings if w.severity == "critical")
        warning_count = sum(1 for w in warnings if w.severity == "warning")

        score -= (critical_count * 0.15 + warning_count * 0.05)

        return max(0.0, min(1.0, round(score, 2)))
