import pytest

pytestmark = pytest.mark.redteam
from backend.verification.contract_validator import ContractValidator
from backend.models.analysis_contract import AnalysisContract

def test_ambiguous_return_rate_without_definition_refuses():
    contract = AnalysisContract(
        question="What is the return rate?",
        datasets_required=["ds_kaggle_orders", "ds_kaggle_returns"],
        columns_required=["order_id"],
        expected_result_type="percentage",
        expected_unit="percent",
        return_definition=None  # Missing explicit return definition
    )
    val_res = ContractValidator.validate_contract(contract)
    assert not val_res.is_valid
    assert "Ambiguous return-rate query lacks an explicit return_definition" in val_res.refusal_reason
