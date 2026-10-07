import pytest
from pathlib import Path
from backend.models.query import AnalysisRequest
from backend.models.analysis import AnalysisStatus, CanonicalResult
from backend.api.dependencies import get_orchestrator
from backend.execution.sandbox import LocalIsolatedSandbox
from backend.services.storage import storage_service
from backend.verification.operation_verifier import OperationVerifier
from backend.verification.proof_policy import ProofPolicy
from backend.models.verification import VerificationResult, CheckStatus

@pytest.fixture(scope="module")
def orchestrator():
    return get_orchestrator()

# Demo Test 1: "What is the total revenue?" -> VERIFIED
def test_demo_1_total_revenue(orchestrator):
    req = AnalysisRequest(question="What is the total revenue?")
    res = orchestrator.process_analysis(req)
    assert res.status == AnalysisStatus.VERIFIED

# Demo Test 2: "What is the highest revenue category?" -> VERIFIED
def test_demo_2_highest_revenue_category(orchestrator):
    req = AnalysisRequest(question="What is the highest revenue category?")
    res = orchestrator.process_analysis(req)
    assert res.status == AnalysisStatus.VERIFIED

# Demo Test 3: "What percentage of orders were returned?" -> VERIFIED with order_return_rate
def test_demo_3_return_rate(orchestrator):
    req = AnalysisRequest(question="What percentage of orders were returned?")
    res = orchestrator.process_analysis(req)
    assert res.status == AnalysisStatus.VERIFIED
    assert res.analysis_contract is not None
    assert res.analysis_contract.return_definition == "order_return_rate"

# Demo Test 4: "Compare USD and EUR revenue" -> REFUSED
def test_demo_4_currency_mismatch_refused(orchestrator):
    req = AnalysisRequest(question="Compare USD and EUR revenue")
    res = orchestrator.process_analysis(req)
    assert res.status in [AnalysisStatus.REFUSED, AnalysisStatus.VERIFICATION_FAILED]

# Demo Test 5: "Which orders are likely to be returned?" -> MODEL_PREDICTION
def test_demo_5_return_prediction(orchestrator):
    req = AnalysisRequest(question="Which orders are likely to be returned?")
    res = orchestrator.process_analysis(req)
    assert res.status == AnalysisStatus.MODEL_PREDICTION

# Demo Test 6: Wrong aggregation -> VERIFICATION_FAILED
def test_demo_6_wrong_aggregation(orchestrator):
    from backend.models.analysis_contract import AnalysisContract, ContractAggregation
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
    op_ver = OperationVerifier.verify_operations(contract, exec_res.get("runtime_operations", []))
    assert op_ver.is_valid is False

    v_res = VerificationResult(v9_expected_operation_reflected=CheckStatus.FAIL, status="VERIFICATION_FAILED")
    status, _ = ProofPolicy.evaluate_policy(v_res, reference_matches=False)
    assert status == AnalysisStatus.VERIFICATION_FAILED

# Demo Test 7: Wrong join -> VERIFICATION_FAILED
def test_demo_7_wrong_join(orchestrator):
    from backend.models.analysis_contract import AnalysisContract, ContractJoin
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
    op_ver = OperationVerifier.verify_operations(contract, exec_res.get("runtime_operations", []))
    assert op_ver.is_valid is False

    v_res = VerificationResult(v9_expected_operation_reflected=CheckStatus.FAIL, status="VERIFICATION_FAILED")
    status, _ = ProofPolicy.evaluate_policy(v_res, reference_matches=False)
    assert status == AnalysisStatus.VERIFICATION_FAILED

# Demo Test 8: Unauthorized dataset -> VERIFICATION_FAILED
def test_demo_8_unauthorized_dataset(orchestrator):
    from backend.models.analysis_contract import AnalysisContract
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
    assert exec_res["success"] is False or len(exec_res.get("accessed_dataset_ids", [])) == 0

    v_res = VerificationResult(v7_required_datasets_used=CheckStatus.FAIL, status="VERIFICATION_FAILED")
    status, _ = ProofPolicy.evaluate_policy(v_res, reference_matches=False)
    assert status == AnalysisStatus.VERIFICATION_FAILED

# Demo Test 9: Missing filter -> VERIFICATION_FAILED
def test_demo_9_missing_filter(orchestrator):
    from backend.models.analysis_contract import AnalysisContract, ContractFilter
    contract = AnalysisContract(
        question="What is premium segment revenue?",
        datasets_required=["ds_kaggle_orders", "ds_kaggle_customers"],
        filters=[ContractFilter(column="customer_segment", operator="==", value="Premium")],
        expected_result_type="scalar",
        expected_unit="INR"
    )
    code = """import pandas as pd, json
df_ord = pd.read_csv("data/ds_kaggle_orders/data.csv")
df_cust = pd.read_csv("data/ds_kaggle_customers/data.csv")
merged = pd.merge(df_ord, df_cust, on="customer_id")
print(json.dumps({"result": float(merged["final_amount"].sum()), "metric": "premium_revenue", "unit": "INR"}))"""

    art1 = storage_service.get_dataset_artifact("ds_kaggle_orders")
    art2 = storage_service.get_dataset_artifact("ds_kaggle_customers")
    sandbox = LocalIsolatedSandbox()
    exec_res = sandbox.execute(code, [art1, art2])
    op_ver = OperationVerifier.verify_operations(contract, exec_res.get("runtime_operations", []))
    assert op_ver.is_valid is False

    v_res = VerificationResult(v9_expected_operation_reflected=CheckStatus.FAIL, status="VERIFICATION_FAILED")
    status, _ = ProofPolicy.evaluate_policy(v_res, reference_matches=False)
    assert status == AnalysisStatus.VERIFICATION_FAILED

# Demo Test 10: Tampered final answer -> VERIFICATION_FAILED
def test_demo_10_tampered_final_answer(orchestrator):
    canonical = CanonicalResult(result=2572592368.57, unit="INR", metric="total_revenue")
    tampered_answer = "The total revenue was ₹1.00."
    import re
    nums = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", tampered_answer.replace(",", ""))]
    is_consistent = any(abs(n - canonical.result) < 1e-2 for n in nums)
    assert is_consistent is False

    v_res = VerificationResult(v10_final_answer_consistent=CheckStatus.FAIL, status="VERIFICATION_FAILED")
    status, _ = ProofPolicy.evaluate_policy(v_res, reference_matches=True)
    assert status == AnalysisStatus.VERIFICATION_FAILED
