import pytest
from backend.models.analysis_contract import AnalysisContract, ContractAggregation, ContractFilter, ContractGroupBy, ContractJoin
from backend.models.analysis import AnalysisStatus
from backend.verification.operation_verifier import OperationVerifier
from backend.api.dependencies import get_orchestrator
from backend.models.query import AnalysisRequest

pytestmark = pytest.mark.redteam

def test_aggregation_mismatch_sum_vs_mean_fails():
    contract = AnalysisContract(
        question="Sum total sales",
        query_type="data_aggregation",
        datasets_required=["ds_redteam_sales"],
        columns_required=["amount"],
        aggregations=[ContractAggregation(operation="sum", column="amount")]
    )
    # Code executed MEAN instead of SUM
    runtime_ops = [{"operation": "aggregate", "column": "amount", "function": "mean"}]
    res = OperationVerifier.verify_operations(contract, runtime_ops)
    assert res.is_valid is False
    assert any("sum" in e and "mean" in e for e in res.errors)

def test_groupby_mismatch_state_vs_city_fails():
    contract = AnalysisContract(
        question="Revenue by state",
        query_type="data_aggregation",
        datasets_required=["ds_redteam_sales"],
        columns_required=["state"],
        group_by=[ContractGroupBy(column="state")]
    )
    # Code executed GROUP BY city instead of state
    runtime_ops = [{"operation": "group_by", "column": "city"}]
    res = OperationVerifier.verify_operations(contract, runtime_ops)
    assert res.is_valid is False
    assert any("state" in e for e in res.errors)

def test_filter_mismatch_premium_vs_basic_fails():
    contract = AnalysisContract(
        question="Premium revenue",
        query_type="data_aggregation",
        datasets_required=["ds_redteam_sales"],
        columns_required=["segment"],
        filters=[ContractFilter(column="segment", operator="==", value="Premium")]
    )
    # Code executed FILTER segment == Basic
    runtime_ops = [{"operation": "filter", "column": "segment", "operator": "==", "value": "Basic"}]
    res = OperationVerifier.verify_operations(contract, runtime_ops)
    assert res.is_valid is False
    assert any("Basic" in e or "Premium" in e for e in res.errors)

def test_join_key_mismatch_customer_id_vs_order_id_fails():
    contract = AnalysisContract(
        question="Joined customer orders",
        query_type="data_aggregation",
        datasets_required=["ds_orders", "ds_customers"],
        columns_required=["customer_id"],
        joins=[ContractJoin(left_dataset="ds_orders", right_dataset="ds_customers", left_column="customer_id", right_column="customer_id")]
    )
    # Code executed JOIN on order_id instead of customer_id
    runtime_ops = [{"operation": "join", "left_column": "order_id", "right_column": "customer_id"}]
    res = OperationVerifier.verify_operations(contract, runtime_ops)
    assert res.is_valid is False
    assert any("customer_id" in e for e in res.errors)

def test_correct_number_with_wrong_operation_fails_pipeline():
    orchestrator = get_orchestrator()
    # Contract expects sum, but code is rigged to execute mean
    req = AnalysisRequest(
        question="What is the total revenue in sales.csv?",
        selected_datasets=["ds_redteam_sales"]
    )
    # Patch generator to produce mean code
    old_gen = orchestrator.code_generator.generate_and_validate
    def mean_code_gen(*args, **kwargs):
        res = old_gen(*args, **kwargs)
        res["code"] = """import pandas as pd
import json
df = pd.read_csv("data/ds_redteam_sales/data.csv")
res_val = float(df["amount"].mean())
print(json.dumps({"result": res_val, "metric": "total_revenue"}))
"""
        return res
    orchestrator.code_generator.generate_and_validate = mean_code_gen

    result = orchestrator.process_analysis(req)
    orchestrator.code_generator.generate_and_validate = old_gen

    assert result.status in [AnalysisStatus.VERIFICATION_FAILED, AnalysisStatus.EXECUTION_FAILED]
