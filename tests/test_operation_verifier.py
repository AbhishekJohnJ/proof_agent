import pytest
from backend.models.analysis_contract import AnalysisContract, ContractAggregation, ContractFilter, ContractGroupBy, ContractJoin, ContractSort
from backend.verification.operation_verifier import OperationVerifier

pytestmark = pytest.mark.unit

def test_operation_verifier_aggregation():
    contract = AnalysisContract(
        question="Sum total revenue",
        query_type="data_aggregation",
        datasets_required=["ds_orders"],
        columns_required=["final_amount"],
        aggregations=[ContractAggregation(operation="sum", column="final_amount")]
    )

    # 1. Correct aggregation -> PASS
    ops_pass = [{"operation": "aggregate", "dataset": "ds_orders", "column": "final_amount", "function": "sum"}]
    res1 = OperationVerifier.verify_operations(contract, ops_pass)
    assert res1.is_valid is True

    # 2. Wrong aggregation (mean instead of sum) -> FAIL
    ops_fail = [{"operation": "aggregate", "dataset": "ds_orders", "column": "final_amount", "function": "mean"}]
    res2 = OperationVerifier.verify_operations(contract, ops_fail)
    assert res2.is_valid is False
    assert any("sum" in e and "mean" in e for e in res2.errors)

def test_operation_verifier_filter():
    contract = AnalysisContract(
        question="Premium customer revenue",
        query_type="data_aggregation",
        datasets_required=["ds_cust"],
        columns_required=["customer_segment"],
        filters=[ContractFilter(column="customer_segment", operator="==", value="Premium")]
    )

    # 3. Correct filter -> PASS
    ops_pass = [{"operation": "filter", "column": "customer_segment", "operator": "==", "value": "Premium"}]
    res1 = OperationVerifier.verify_operations(contract, ops_pass)
    assert res1.is_valid is True

    # 4. Wrong filter value -> FAIL
    ops_fail = [{"operation": "filter", "column": "customer_segment", "operator": "==", "value": "Basic"}]
    res2 = OperationVerifier.verify_operations(contract, ops_fail)
    assert res2.is_valid is False
    assert any("Basic" in e or "Premium" in e for e in res2.errors)

def test_operation_verifier_groupby():
    contract = AnalysisContract(
        question="Revenue by state",
        query_type="data_aggregation",
        datasets_required=["ds_cust"],
        columns_required=["state"],
        group_by=[ContractGroupBy(column="state")]
    )

    # 5. Correct groupby -> PASS
    ops_pass = [{"operation": "group_by", "column": "state"}]
    res1 = OperationVerifier.verify_operations(contract, ops_pass)
    assert res1.is_valid is True

    # 6. Wrong groupby -> FAIL
    ops_fail = [{"operation": "group_by", "column": "city"}]
    res2 = OperationVerifier.verify_operations(contract, ops_fail)
    assert res2.is_valid is False
    assert any("state" in e for e in res2.errors)

def test_operation_verifier_join():
    contract = AnalysisContract(
        question="Joined query",
        query_type="data_aggregation",
        datasets_required=["ds_orders", "ds_cust"],
        columns_required=["customer_id"],
        joins=[ContractJoin(left_dataset="ds_orders", right_dataset="ds_cust", left_column="customer_id", right_column="customer_id")]
    )

    # 7. Correct join -> PASS
    ops_pass = [{"operation": "join", "left_column": "customer_id", "right_column": "customer_id"}]
    res1 = OperationVerifier.verify_operations(contract, ops_pass)
    assert res1.is_valid is True

    # 8. Wrong join key -> FAIL
    ops_fail = [{"operation": "join", "left_column": "order_id", "right_column": "customer_id"}]
    res2 = OperationVerifier.verify_operations(contract, ops_fail)
    assert res2.is_valid is False
    assert any("customer_id" in e for e in res2.errors)

def test_operation_verifier_sort():
    contract = AnalysisContract(
        question="Sorted query",
        query_type="data_aggregation",
        datasets_required=["ds_orders"],
        columns_required=["final_amount"],
        sorting=[ContractSort(column="final_amount", order="desc")]
    )

    # 9. Correct sort -> PASS
    ops_pass = [{"operation": "sort", "column": "final_amount", "order": "desc"}]
    res1 = OperationVerifier.verify_operations(contract, ops_pass)
    assert res1.is_valid is True

    # 10. Wrong sort -> FAIL
    ops_fail = [{"operation": "sort", "column": "created_at", "order": "desc"}]
    res2 = OperationVerifier.verify_operations(contract, ops_fail)
    assert res2.is_valid is False
    assert any("final_amount" in e for e in res2.errors)
