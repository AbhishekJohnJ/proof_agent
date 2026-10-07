import pytest
from backend.models.query import AnalysisRequest
from backend.models.analysis import AnalysisStatus
from backend.api.dependencies import get_orchestrator
from backend.models.analysis_contract import AnalysisContract, ContractAggregation

def test_wrong_number_discrepancy_fails():
    orchestrator = get_orchestrator()
    req = AnalysisRequest(
        question="What is the total sales amount?",
        selected_datasets=["ds_redteam_sales"]
    )
    res = orchestrator.process_analysis(req)
    
    # Intentionally corrupt the reference or generated value comparison
    if res.canonical_result:
        res.canonical_result.result = 999999999.0
        # Re-evaluate verification policy
        from backend.verification.proof_policy import ProofPolicy
        res.verification.v3_output_valid_canonical = "FAIL"
        status, _ = ProofPolicy.evaluate_policy(res.verification, reference_matches=False)
        assert status != AnalysisStatus.VERIFIED
