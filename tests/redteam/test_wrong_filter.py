import pytest

pytestmark = pytest.mark.redteam
from backend.verification.contract_validator import ContractValidator
from backend.models.analysis_contract import AnalysisContract, ContractFilter

def test_invalid_filter_column_refuses():
    contract = AnalysisContract(
        question="What is sales for premium segment?",
        datasets_required=["ds_kaggle_customers"],
        columns_required=["state"],
        filters=[
            ContractFilter(
                dataset="ds_kaggle_customers",
                column="fake_segment_col",
                operator="==",
                value="Premium"
            )
        ],
        expected_result_type="scalar",
        expected_unit="INR"
    )
    val_res = ContractValidator.validate_contract(contract)
    assert not val_res.is_valid
    assert "Invalid filter column" in val_res.refusal_reason or "Column resolution failed" in val_res.refusal_reason
