import pytest

pytestmark = pytest.mark.redteam
from backend.verification.contract_validator import ContractValidator
from backend.models.analysis_contract import AnalysisContract, ContractAggregation

def test_invalid_aggregation_column_refuses():
    contract = AnalysisContract(
        question="What is total sales?",
        datasets_required=["ds_kaggle_orders"],
        columns_required=["final_amount"],
        aggregations=[
            ContractAggregation(
                dataset="ds_kaggle_orders",
                column="non_existent_column",
                operation="sum"
            )
        ],
        expected_result_type="scalar",
        expected_unit="INR"
    )
    val_res = ContractValidator.validate_contract(contract)
    assert not val_res.is_valid
    assert "Invalid aggregation column" in val_res.refusal_reason or "Column resolution failed" in val_res.refusal_reason
