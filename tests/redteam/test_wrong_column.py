import pytest

pytestmark = pytest.mark.redteam
from backend.models.query import AnalysisRequest
from backend.models.analysis import AnalysisStatus
from backend.api.dependencies import get_orchestrator
from backend.verification.contract_validator import ContractValidator
from backend.models.analysis_contract import AnalysisContract

def test_missing_or_wrong_column_refuses():
    contract = AnalysisContract(
        question="What is the total sales amount?",
        datasets_required=["ds_redteam_sales"],
        columns_required=["non_existent_column_xyz"],
        expected_result_type="scalar",
        expected_unit="INR"
    )
    val_res = ContractValidator.validate_contract(contract)
    assert not val_res.is_valid
    assert "non_existent_column_xyz" in val_res.refusal_reason
