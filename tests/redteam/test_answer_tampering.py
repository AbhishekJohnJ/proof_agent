import pytest

pytestmark = pytest.mark.redteam
from backend.models.verification import CheckStatus, VerificationResult
from backend.models.analysis import AnalysisStatus
from backend.models.analysis import CanonicalResult
from backend.verification.proof_policy import ProofPolicy

def test_tampered_answer_fails_v10():
    canonical_res = CanonicalResult(
        result=2572592368.57,
        metric="total_revenue",
        unit="INR"
    )
    v_res = VerificationResult(
        v1_code_executed=CheckStatus.PASS,
        v2_output_exists=CheckStatus.PASS,
        v3_output_valid_canonical=CheckStatus.PASS,
        v4_result_type_matched=CheckStatus.PASS,
        v5_result_finite_valid=CheckStatus.PASS,
        v6_reproducible=CheckStatus.PASS,
        v7_required_datasets_used=CheckStatus.PASS,
        v8_required_columns_used=CheckStatus.PASS,
        v9_expected_operation_reflected=CheckStatus.PASS,
        v10_final_answer_consistent=CheckStatus.FAIL,  # Tampered answer numerical claim
        v11_unit_matched=CheckStatus.PASS,
        v12_quality_requirements_satisfied=CheckStatus.PASS
    )

    status, _ = ProofPolicy.evaluate_policy(v_res, reference_matches=True)
    assert status == AnalysisStatus.VERIFICATION_FAILED
