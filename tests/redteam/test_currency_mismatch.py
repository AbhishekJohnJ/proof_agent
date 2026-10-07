import pytest

pytestmark = pytest.mark.redteam
from backend.verification.contract_validator import ContractValidator
from backend.models.analysis_contract import AnalysisContract

def test_unsupported_currency_refuses():
    contract = AnalysisContract(
        question="Compare USD and EUR revenue",
        datasets_required=["ds_kaggle_orders"],
        columns_required=["final_amount"],
        expected_result_type="scalar",
        expected_unit="BTC"  # Unsupported currency / unit
    )
    val_res = ContractValidator.validate_contract(contract)
    assert not val_res.is_valid
    assert "Unsupported or unverified unit" in val_res.refusal_reason
