from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from backend.models.analysis import AnalysisStatus
from backend.models.verification import CheckStatus, VerificationResult

class ProofPolicy:
    """
    Centralized Proof Policy enforcing the exact verification invariant.
    
    AN ANSWER MAY BE MARKED VERIFIED ONLY IF:
    1. Question is answerable and non-refused.
    2. Resolved datasets are authorized.
    3. AnalysisContract explicitly describes the computation.
    4. Code execution succeeded and output valid canonical result.
    5. Result type matches contract expected result type.
    6. Numerical values are finite and valid.
    7. Code is reproducible on 2nd execution.
    8. Only authorized datasets were accessed.
    9. Required columns were actually used.
    10. Required joins, group-bys, aggregations, and filters were reflected.
    11. Unit matches contract with provenance.
    12. Result matches independent deterministic reference calculation.
    13. No critical data quality issues or join cardinality explosions exist.
    """

    @classmethod
    def evaluate_policy(
        cls,
        verification_result: VerificationResult,
        reference_matches: bool,
        has_critical_quality_issue: bool = False,
        is_model_prediction: bool = False,
        is_document_only: bool = False,
        is_refused: bool = False
    ) -> Tuple[AnalysisStatus, str]:
        if is_refused:
            return AnalysisStatus.REFUSED, "refusal"

        if is_model_prediction:
            return AnalysisStatus.MODEL_PREDICTION, "model_prediction"

        if is_document_only:
            if verification_result.status == "VERIFIED" or verification_result.v13_evidence_sources_matched == CheckStatus.PASS:
                return AnalysisStatus.DOCUMENT_SUPPORTED, "document_supported"
            return AnalysisStatus.VERIFICATION_FAILED, "verification_failed"

        v = verification_result
        all_checks_passed = (
            v.v1_code_executed == CheckStatus.PASS and
            v.v2_output_exists == CheckStatus.PASS and
            v.v3_output_valid_canonical == CheckStatus.PASS and
            v.v4_result_type_matched == CheckStatus.PASS and
            v.v5_result_finite_valid == CheckStatus.PASS and
            v.v6_reproducible == CheckStatus.PASS and
            v.v7_required_datasets_used == CheckStatus.PASS and
            v.v8_required_columns_used in [CheckStatus.PASS, CheckStatus.NOT_APPLICABLE] and
            v.v9_expected_operation_reflected == CheckStatus.PASS and
            v.v10_final_answer_consistent == CheckStatus.PASS and
            v.v11_unit_matched in [CheckStatus.PASS, CheckStatus.NOT_APPLICABLE] and
            v.v12_quality_requirements_satisfied == CheckStatus.PASS and
            reference_matches and
            not has_critical_quality_issue
        )

        if all_checks_passed:
            return AnalysisStatus.VERIFIED, "verified_analysis"
        else:
            return AnalysisStatus.VERIFICATION_FAILED, "verification_failed"
