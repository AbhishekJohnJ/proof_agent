import pytest

pytestmark = pytest.mark.redteam
from backend.verification.contract_validator import ContractValidator
from backend.models.analysis_contract import AnalysisContract, ContractJoin

def test_invalid_join_key_refuses():
    contract = AnalysisContract(
        question="What is the sales by customer?",
        datasets_required=["ds_kaggle_orders", "ds_kaggle_customers"],
        columns_required=["final_amount"],
        joins=[
            ContractJoin(
                left_dataset="ds_kaggle_orders",
                left_column="invalid_join_key",
                right_dataset="ds_kaggle_customers",
                right_column="customer_id"
            )
        ],
        expected_result_type="scalar",
        expected_unit="INR"
    )
    val_res = ContractValidator.validate_contract(contract)
    assert not val_res.is_valid
    assert "Invalid join" in val_res.refusal_reason or "Column resolution failed" in val_res.refusal_reason
