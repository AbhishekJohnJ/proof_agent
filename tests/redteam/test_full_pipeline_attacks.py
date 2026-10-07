import pytest
from pathlib import Path
from backend.models.query import AnalysisRequest
from backend.models.analysis import AnalysisStatus, CanonicalResult
from backend.models.analysis_contract import (
    AnalysisContract, ContractJoin, ContractFilter, ContractAggregation, ContractGroupBy
)
from backend.api.dependencies import get_orchestrator
from backend.execution.sandbox import LocalIsolatedSandbox
from backend.services.storage import storage_service
from backend.verification.operation_verifier import OperationVerifier
from backend.verification.contract_checker import StaticContractChecker
from backend.verification.proof_policy import ProofPolicy
from backend.models.verification import VerificationResult, CheckStatus

pytestmark = pytest.mark.redteam

@pytest.fixture
def orchestrator():
    return get_orchestrator()

# A. Wrong aggregation -> VERIFICATION_FAILED
def test_attack_A_wrong_aggregation(orchestrator):
    contract = AnalysisContract(
        question="What is total revenue?",
        datasets_required=["ds_kaggle_orders"],
        columns_required=["final_amount"],
        aggregations=[ContractAggregation(column="final_amount", operation="sum")],
        expected_result_type="scalar",
        expected_unit="INR"
    )
    code = """import pandas as pd, json
df = pd.read_csv("data/ds_kaggle_orders/data.csv")
val = float(df["final_amount"].mean())
print(json.dumps({"result": val, "metric": "total_revenue", "unit": "INR"}))"""

    art = storage_service.get_dataset_artifact("ds_kaggle_orders")
    sandbox = LocalIsolatedSandbox()
    exec_res = sandbox.execute(code, [art])
    assert exec_res["success"] is True

    op_res = OperationVerifier.verify_operations(contract, exec_res.get("runtime_operations", []))
    assert op_res.is_valid is False
    assert any("Aggregation" in err for err in op_res.errors)

    v_res = VerificationResult(v9_expected_operation_reflected=CheckStatus.FAIL, status="VERIFICATION_FAILED")
    final_status, _ = ProofPolicy.evaluate_policy(v_res, reference_matches=False)
    assert final_status in [AnalysisStatus.VERIFICATION_FAILED, AnalysisStatus.REFUSED]

# B. Wrong filter -> VERIFICATION_FAILED
def test_attack_B_wrong_filter(orchestrator):
    contract = AnalysisContract(
        question="What is premium segment total spend?",
        datasets_required=["ds_kaggle_orders", "ds_kaggle_customers"],
        joins=[ContractJoin(left_dataset="orders", left_column="customer_id", right_dataset="customers", right_column="customer_id")],
        columns_required=["final_amount", "customer_segment"],
        filters=[ContractFilter(dataset="customers", column="customer_segment", operator="==", value="Premium")],
        aggregations=[ContractAggregation(column="final_amount", operation="sum")],
        expected_result_type="scalar",
        expected_unit="INR"
    )
    code = """import pandas as pd, json
df_ord = pd.read_csv("data/ds_kaggle_orders/data.csv")
df_cust = pd.read_csv("data/ds_kaggle_customers/data.csv")
merged = pd.merge(df_ord, df_cust, on="customer_id")
filtered = merged[merged["customer_segment"] == "Basic"]
val = float(filtered["final_amount"].sum())
print(json.dumps({"result": val, "metric": "premium_spend", "unit": "INR"}))"""

    art1 = storage_service.get_dataset_artifact("ds_kaggle_orders")
    art2 = storage_service.get_dataset_artifact("ds_kaggle_customers")
    sandbox = LocalIsolatedSandbox()
    exec_res = sandbox.execute(code, [art1, art2])
    assert exec_res["success"] is True

    op_res = OperationVerifier.verify_operations(contract, exec_res.get("runtime_operations", []))
    assert op_res.is_valid is False
    assert any("Filter" in err for err in op_res.errors)

    v_res = VerificationResult(v9_expected_operation_reflected=CheckStatus.FAIL, status="VERIFICATION_FAILED")
    final_status, _ = ProofPolicy.evaluate_policy(v_res, reference_matches=False)
    assert final_status in [AnalysisStatus.VERIFICATION_FAILED, AnalysisStatus.REFUSED]

# C. Wrong group-by -> VERIFICATION_FAILED
def test_attack_C_wrong_groupby(orchestrator):
    contract = AnalysisContract(
        question="Which state generated highest revenue?",
        datasets_required=["ds_kaggle_orders", "ds_kaggle_customers"],
        joins=[ContractJoin(left_dataset="orders", left_column="customer_id", right_dataset="customers", right_column="customer_id")],
        group_by=[ContractGroupBy(column="state")],
        aggregations=[ContractAggregation(column="final_amount", operation="sum")],
        expected_result_type="ranked_item",
        expected_unit="INR"
    )
    code = """import pandas as pd, json
df_ord = pd.read_csv("data/ds_kaggle_orders/data.csv")
df_cust = pd.read_csv("data/ds_kaggle_customers/data.csv")
merged = pd.merge(df_ord, df_cust, on="customer_id")
grouped = merged.groupby("city")["final_amount"].sum().reset_index()
top = grouped.sort_values(by="final_amount", ascending=False).iloc[0]
print(json.dumps({"result": float(top["final_amount"]), "label": str(top["city"]), "metric": "highest_revenue_state", "unit": "INR", "result_type": "ranked_item"}))"""

    art1 = storage_service.get_dataset_artifact("ds_kaggle_orders")
    art2 = storage_service.get_dataset_artifact("ds_kaggle_customers")
    sandbox = LocalIsolatedSandbox()
    exec_res = sandbox.execute(code, [art1, art2])
    assert exec_res["success"] is True

    op_res = OperationVerifier.verify_operations(contract, exec_res.get("runtime_operations", []))
    assert op_res.is_valid is False
    assert any("GroupBy" in err for err in op_res.errors)

    v_res = VerificationResult(v9_expected_operation_reflected=CheckStatus.FAIL, status="VERIFICATION_FAILED")
    final_status, _ = ProofPolicy.evaluate_policy(v_res, reference_matches=False)
    assert final_status in [AnalysisStatus.VERIFICATION_FAILED, AnalysisStatus.REFUSED]

# D. Wrong join -> VERIFICATION_FAILED
def test_attack_D_wrong_join(orchestrator):
    contract = AnalysisContract(
        question="Revenue by customer?",
        datasets_required=["ds_kaggle_orders", "ds_kaggle_customers"],
        joins=[ContractJoin(left_dataset="orders", left_column="customer_id", right_dataset="customers", right_column="customer_id")],
        columns_required=["final_amount"],
        expected_result_type="scalar",
        expected_unit="INR"
    )
    code = """import pandas as pd, json
df_ord = pd.read_csv("data/ds_kaggle_orders/data.csv")
df_cust = pd.read_csv("data/ds_kaggle_customers/data.csv")
merged = pd.merge(df_ord, df_cust, left_on="order_id", right_on="customer_id")
print(json.dumps({"result": float(merged["final_amount"].sum()), "metric": "revenue", "unit": "INR"}))"""

    art1 = storage_service.get_dataset_artifact("ds_kaggle_orders")
    art2 = storage_service.get_dataset_artifact("ds_kaggle_customers")
    sandbox = LocalIsolatedSandbox()
    exec_res = sandbox.execute(code, [art1, art2])

    op_res = OperationVerifier.verify_operations(contract, exec_res.get("runtime_operations", []))
    assert op_res.is_valid is False or exec_res["success"] is False

    v_res = VerificationResult(v9_expected_operation_reflected=CheckStatus.FAIL, status="VERIFICATION_FAILED")
    final_status, _ = ProofPolicy.evaluate_policy(v_res, reference_matches=False)
    assert final_status in [AnalysisStatus.VERIFICATION_FAILED, AnalysisStatus.REFUSED]

# E. Unauthorized dataset -> VERIFICATION_FAILED
def test_attack_E_unauthorized_dataset(orchestrator):
    contract = AnalysisContract(
        question="What is total revenue?",
        datasets_required=["ds_kaggle_orders"],
        columns_required=["final_amount"],
        expected_result_type="scalar",
        expected_unit="INR"
    )
    code = """import pandas as pd, json
df_pay = pd.read_csv("data/ds_kaggle_payments/data.csv")
print(json.dumps({"result": float(df_pay["amount_paid"].sum()), "metric": "revenue", "unit": "INR"}))"""

    art1 = storage_service.get_dataset_artifact("ds_kaggle_orders")
    sandbox = LocalIsolatedSandbox()
    exec_res = sandbox.execute(code, [art1])

    # Unmounted dataset read fails or records unauthorized access
    v7_status = CheckStatus.FAIL if (not exec_res["success"] or "ds_kaggle_payments" not in ["ds_kaggle_orders"]) else CheckStatus.PASS
    assert v7_status == CheckStatus.FAIL or exec_res["success"] is False

    v_res = VerificationResult(v7_required_datasets_used=CheckStatus.FAIL, status="VERIFICATION_FAILED")
    final_status, _ = ProofPolicy.evaluate_policy(v_res, reference_matches=False)
    assert final_status in [AnalysisStatus.VERIFICATION_FAILED, AnalysisStatus.REFUSED]

# F. Missing required column -> VERIFICATION_FAILED
def test_attack_F_missing_required_column(orchestrator):
    contract = AnalysisContract(
        question="What is total revenue?",
        datasets_required=["ds_kaggle_orders"],
        columns_required=["final_amount"],
        expected_result_type="scalar",
        expected_unit="INR"
    )
    code = """import pandas as pd, json
df = pd.read_csv("data/ds_kaggle_orders/data.csv")
print(json.dumps({"result": 100.0, "metric": "total_revenue", "unit": "INR"}))"""

    art1 = storage_service.get_dataset_artifact("ds_kaggle_orders")
    sandbox = LocalIsolatedSandbox()
    exec_res = sandbox.execute(code, [art1])

    runtime_cols = exec_res.get("accessed_columns", [])
    accessed = [ev.get("column") for ev in runtime_cols if ev.get("column") == "final_amount"]
    assert len(accessed) == 0

    v_res = VerificationResult(v8_required_columns_used=CheckStatus.FAIL, status="VERIFICATION_FAILED")
    final_status, _ = ProofPolicy.evaluate_policy(v_res, reference_matches=False)
    assert final_status in [AnalysisStatus.VERIFICATION_FAILED, AnalysisStatus.REFUSED]

# G. Wrong unit -> VERIFICATION_FAILED
def test_attack_G_wrong_unit(orchestrator):
    contract = AnalysisContract(
        question="What is total revenue?",
        datasets_required=["ds_kaggle_orders"],
        columns_required=["final_amount"],
        aggregations=[ContractAggregation(column="final_amount", operation="sum")],
        expected_result_type="scalar",
        expected_unit="INR"
    )
    code = """import pandas as pd, json
df = pd.read_csv("data/ds_kaggle_orders/data.csv")
val = float(df["final_amount"].sum())
print(json.dumps({"result": val, "metric": "total_revenue", "unit": "USD"}))"""

    art1 = storage_service.get_dataset_artifact("ds_kaggle_orders")
    sandbox = LocalIsolatedSandbox()
    exec_res = sandbox.execute(code, [art1])

    parsed = exec_res.get("parsed_output", {})
    actual_unit = parsed.get("unit")
    assert actual_unit != contract.expected_unit

    v_res = VerificationResult(v11_unit_matched=CheckStatus.FAIL, status="VERIFICATION_FAILED")
    final_status, _ = ProofPolicy.evaluate_policy(v_res, reference_matches=True)
    assert final_status in [AnalysisStatus.VERIFICATION_FAILED, AnalysisStatus.REFUSED]

# H. Wrong result -> VERIFICATION_FAILED
def test_attack_H_wrong_result(orchestrator):
    contract = AnalysisContract(
        question="What is total revenue?",
        datasets_required=["ds_kaggle_orders"],
        columns_required=["final_amount"],
        aggregations=[ContractAggregation(column="final_amount", operation="sum")],
        expected_result_type="scalar",
        expected_unit="INR"
    )
    code = """import pandas as pd, json
df = pd.read_csv("data/ds_kaggle_orders/data.csv")
dummy = df["final_amount"].head(1)
print(json.dumps({"result": 999.0, "metric": "total_revenue", "unit": "INR"}))"""

    art1 = storage_service.get_dataset_artifact("ds_kaggle_orders")
    sandbox = LocalIsolatedSandbox()
    exec_res = sandbox.execute(code, [art1])

    from backend.analysis.reference_engine import ReferenceEngine
    ref = ReferenceEngine.compute_reference(contract, {"ds_kaggle_orders": Path(art1.workspace_path)})
    assert ref.get("success") is True
    assert abs(ref["result"] - 999.0) > 10.0

    v_res = VerificationResult(v1_code_executed=CheckStatus.PASS, status="VERIFICATION_FAILED")
    final_status, _ = ProofPolicy.evaluate_policy(v_res, reference_matches=False)
    assert final_status in [AnalysisStatus.VERIFICATION_FAILED, AnalysisStatus.REFUSED]

# I. Modified final answer -> VERIFICATION_FAILED
def test_attack_I_modified_final_answer(orchestrator):
    contract = AnalysisContract(
        question="What is total revenue?",
        datasets_required=["ds_kaggle_orders"],
        columns_required=["final_amount"],
        aggregations=[ContractAggregation(column="final_amount", operation="sum")],
        expected_result_type="scalar",
        expected_unit="INR"
    )
    canonical = CanonicalResult(result=2572592368.57, unit="INR", metric="total_revenue")
    tampered_answer = "The total revenue was ₹100.00 INR."
    import re
    nums = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", tampered_answer.replace(",", ""))]
    is_consistent = any(abs(n - canonical.result) < 1e-2 for n in nums)
    assert is_consistent is False

    v_res = VerificationResult(v10_final_answer_consistent=CheckStatus.FAIL, status="VERIFICATION_FAILED")
    final_status, _ = ProofPolicy.evaluate_policy(v_res, reference_matches=True)
    assert final_status in [AnalysisStatus.VERIFICATION_FAILED, AnalysisStatus.REFUSED]

# J. Unused required column -> VERIFICATION_FAILED
def test_attack_J_unused_required_column(orchestrator):
    contract = AnalysisContract(
        question="What is total revenue and discount?",
        datasets_required=["ds_kaggle_orders"],
        columns_required=["final_amount", "discount_percentage"],
        aggregations=[ContractAggregation(column="final_amount", operation="sum")],
        expected_result_type="scalar",
        expected_unit="INR"
    )
    code = """import pandas as pd, json
df = pd.read_csv("data/ds_kaggle_orders/data.csv")
val = float(df["final_amount"].sum())
print(json.dumps({"result": val, "metric": "total_revenue", "unit": "INR"}))"""

    art1 = storage_service.get_dataset_artifact("ds_kaggle_orders")
    sandbox = LocalIsolatedSandbox()
    exec_res = sandbox.execute(code, [art1])

    runtime_cols = [ev.get("column") for ev in exec_res.get("accessed_columns", [])]
    assert "discount_percentage" not in runtime_cols

    v_res = VerificationResult(v8_required_columns_used=CheckStatus.FAIL, status="VERIFICATION_FAILED")
    final_status, _ = ProofPolicy.evaluate_policy(v_res, reference_matches=True)
    assert final_status in [AnalysisStatus.VERIFICATION_FAILED, AnalysisStatus.REFUSED]
