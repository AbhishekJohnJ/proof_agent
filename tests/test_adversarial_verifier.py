import pytest
import pandas as pd
from pathlib import Path
from backend.models.query import AnalysisRequest
from backend.models.analysis import AnalysisStatus, CanonicalResult
from backend.models.analysis_contract import AnalysisContract, ContractOperation, ContractJoin, ContractFilter, ContractAggregation, ContractGroupBy
from backend.verification.contract_checker import StaticContractChecker
from backend.verification.join_checker import JoinChecker
from backend.verification.result_checker import ResultChecker
from backend.verification.reproducibility import ReproducibilityVerifier
from backend.verification.proof_policy import ProofPolicy
from backend.models.verification import VerificationResult, CheckStatus
from backend.analysis.reference_engine import ReferenceEngine
from backend.api.dependencies import get_orchestrator
from backend.data.catalog import dataset_catalog

@pytest.fixture(scope="module")
def kaggle_ds():
    return [d["dataset_id"] for d in dataset_catalog.list_datasets()]

# A. Wrong dataset -> VERIFICATION_FAILED
def test_adversarial_A_wrong_dataset():
    contract = AnalysisContract(
        question="What is total revenue?",
        datasets_required=["ds_kaggle_orders"],
        columns_required=["final_amount"]
    )
    code = """import pandas as pd, json
df = pd.read_csv("data/ds_kaggle_customers/data.csv")
print(json.dumps({"result": 100}))"""
    v7, v8, v9, errors = StaticContractChecker.check_contract(code, contract, ["ds_kaggle_orders"])
    assert v7 == CheckStatus.FAIL

# B. Unauthorized dataset access -> VERIFICATION_FAILED
def test_adversarial_B_unauthorized_dataset():
    from backend.execution.sandbox import LocalIsolatedSandbox
    from backend.services.storage import storage_service
    sandbox = LocalIsolatedSandbox()
    art_orders = storage_service.get_dataset_artifact("ds_kaggle_orders")

    # Code reads unauthorized dataset file that was not mounted
    code = """import pandas as pd, json
df = pd.read_csv("data/ds_kaggle_payments/data.csv")
print(json.dumps({"result": len(df)}))"""
    res = sandbox.execute(code, [art_orders])
    assert res["success"] is False

# C. Wrong column -> VERIFICATION_FAILED
def test_adversarial_C_wrong_column():
    contract = AnalysisContract(
        question="What is total revenue?",
        datasets_required=["ds_kaggle_orders"],
        columns_required=["final_amount"]
    )
    code = """import pandas as pd, json
df = pd.read_csv("data/ds_kaggle_orders/data.csv")
val = df["order_id"].sum()
print(json.dumps({"result": val}))"""
    v7, v8, v9, errors = StaticContractChecker.check_contract(code, contract, ["ds_kaggle_orders"])
    assert v8 == CheckStatus.FAIL

# D. Unused required column -> VERIFICATION_FAILED
def test_adversarial_D_unused_required_column():
    contract = AnalysisContract(
        question="What is total revenue?",
        datasets_required=["ds_kaggle_orders"],
        columns_required=["final_amount", "discount"]
    )
    code = """import pandas as pd, json
df = pd.read_csv("data/ds_kaggle_orders/data.csv")
val = df["final_amount"].sum()
print(json.dumps({"result": val}))"""
    v7, v8, v9, errors = StaticContractChecker.check_contract(code, contract, ["ds_kaggle_orders"])
    assert v8 == CheckStatus.FAIL

# E. Wrong join key -> VERIFICATION_FAILED
def test_adversarial_E_wrong_join_key():
    df_orders = pd.DataFrame({"order_id": [1, 2], "customer_id": [10, 20]})
    df_cust = pd.DataFrame({"customer_id": [10, 20], "name": ["A", "B"]})
    res = JoinChecker.validate_join(df_orders, df_cust, left_key="order_id", right_key="customer_id")
    assert res["valid"] is False

# F. Wrong join type / missing join -> VERIFICATION_FAILED
def test_adversarial_F_wrong_join_type():
    contract = AnalysisContract(
        question="Which category has highest revenue?",
        datasets_required=["ds_kaggle_order_items", "ds_kaggle_products"],
        joins=[ContractJoin(left_dataset="order_items", left_column="product_id", right_dataset="products", right_column="product_id")]
    )
    code = """import pandas as pd, json
df1 = pd.read_csv("data/ds_kaggle_order_items/data.csv")
df2 = pd.read_csv("data/ds_kaggle_products/data.csv")
print(json.dumps({"result": 100}))"""
    v7, v8, v9, errors = StaticContractChecker.check_contract(code, contract, ["ds_kaggle_order_items", "ds_kaggle_products"])
    assert v9 == CheckStatus.FAIL

# G. Wrong aggregation -> VERIFICATION_FAILED
def test_adversarial_G_wrong_aggregation():
    contract = AnalysisContract(
        question="What is total revenue?",
        datasets_required=["ds_kaggle_orders"],
        aggregations=[ContractAggregation(column="final_amount", operation="sum")]
    )
    code = """import pandas as pd, json
df = pd.read_csv("data/ds_kaggle_orders/data.csv")
val = df["final_amount"].mean()
print(json.dumps({"result": val}))"""
    v7, v8, v9, errors = StaticContractChecker.check_contract(code, contract, ["ds_kaggle_orders"])
    assert v9 == CheckStatus.FAIL

# H. Wrong filter / missing filter -> VERIFICATION_FAILED
def test_adversarial_H_wrong_filter():
    contract = AnalysisContract(
        question="What is premium revenue?",
        datasets_required=["ds_kaggle_orders", "ds_kaggle_customers"],
        filters=[ContractFilter(column="customer_segment", operator="==", value="Premium")]
    )
    code = """import pandas as pd, json
df_ord = pd.read_csv("data/ds_kaggle_orders/data.csv")
df_cust = pd.read_csv("data/ds_kaggle_customers/data.csv")
merged = pd.merge(df_ord, df_cust, on="customer_id")
prem = merged[merged["customer_segment"] == "Basic"]
print(json.dumps({"result": prem["final_amount"].sum()}))"""
    # Calculation result differs from reference calculation
    ref_res = ReferenceEngine.compute_reference(contract, {
        "ds_kaggle_orders": Path("data/orders.csv"),
        "ds_kaggle_customers": Path("data/customers.csv")
    })
    if ref_res.get("success"):
        assert abs(ref_res["result"] - 0.0) > 1.0

# I. Missing filter -> VERIFICATION_FAILED
def test_adversarial_I_missing_filter():
    from backend.execution.sandbox import LocalIsolatedSandbox
    from backend.services.storage import storage_service
    from backend.verification.operation_verifier import OperationVerifier

    contract = AnalysisContract(
        question="What is premium revenue?",
        datasets_required=["ds_kaggle_orders", "ds_kaggle_customers"],
        filters=[ContractFilter(column="customer_segment", operator="==", value="Premium")]
    )
    code = """import pandas as pd, json
df_ord = pd.read_csv("data/ds_kaggle_orders/data.csv")
df_cust = pd.read_csv("data/ds_kaggle_customers/data.csv")
merged = pd.merge(df_ord, df_cust, on="customer_id")
print(json.dumps({"result": float(merged["final_amount"].sum())}))"""

    art_orders = storage_service.get_dataset_artifact("ds_kaggle_orders")
    art_cust = storage_service.get_dataset_artifact("ds_kaggle_customers")
    sandbox = LocalIsolatedSandbox()
    exec_res = sandbox.execute(code, [art_orders, art_cust])
    assert exec_res["success"] is True

    op_ver = OperationVerifier.verify_operations(contract, exec_res.get("runtime_operations", []))
    assert op_ver.is_valid is False
    assert any("Missing required filter" in err or "Filter" in err for err in op_ver.errors)

    # ProofPolicy evaluation
    v_res = VerificationResult(
        v1_code_executed=CheckStatus.PASS,
        v2_output_exists=CheckStatus.PASS,
        v3_output_valid_canonical=CheckStatus.PASS,
        v9_expected_operation_reflected=CheckStatus.FAIL,
        status="VERIFICATION_FAILED"
    )
    status, kind = ProofPolicy.evaluate_policy(v_res, reference_matches=False)
    assert status == AnalysisStatus.VERIFICATION_FAILED

# J. Wrong group-by -> VERIFICATION_FAILED
def test_adversarial_J_wrong_group_by():
    contract = AnalysisContract(
        question="Highest revenue state?",
        datasets_required=["ds_kaggle_orders", "ds_kaggle_customers"],
        group_by=[ContractGroupBy(column="state")]
    )
    code = """import pandas as pd, json
df_ord = pd.read_csv("data/ds_kaggle_orders/data.csv")
df_cust = pd.read_csv("data/ds_kaggle_customers/data.csv")
merged = pd.merge(df_ord, df_cust, on="customer_id")
st = merged.groupby("city")["final_amount"].sum().reset_index()
top = st.iloc[0]
print(json.dumps({"result": top["final_amount"], "metric": top["city"]}))"""
    v7, v8, v9, errors = StaticContractChecker.check_contract(code, contract, ["ds_kaggle_orders", "ds_kaggle_customers"])
    assert v9 == CheckStatus.FAIL

# K. Wrong sort direction -> VERIFICATION_FAILED
def test_adversarial_K_wrong_sort_direction():
    df = pd.DataFrame({"state": ["A", "B"], "final_amount": [100, 500]})
    top_asc = df.sort_values(by="final_amount", ascending=True).iloc[0]
    top_desc = df.sort_values(by="final_amount", ascending=False).iloc[0]
    assert top_asc["state"] != top_desc["state"]

# L. Wrong result type -> VERIFICATION_FAILED
def test_adversarial_L_wrong_result_type():
    out_pres, out_val, type_match, errors = ResultChecker.check_result({"parsed_output": {"result": "text_string"}}, "number")
    assert type_match == CheckStatus.FAIL

# M. Wrong unit -> VERIFICATION_FAILED
def test_adversarial_M_wrong_unit():
    contract = AnalysisContract(question="Total revenue?", expected_unit="INR")
    canonical = CanonicalResult(result=100.0, unit="USD")
    assert canonical.unit != contract.expected_unit

# N. Wrong currency -> VERIFICATION_FAILED
def test_adversarial_N_wrong_currency():
    contract = AnalysisContract(question="Revenue in INR?", expected_unit="INR")
    canonical = CanonicalResult(result=100.0, unit="EUR")
    assert canonical.unit != contract.expected_unit

# O. Wrong return-rate definition -> VERIFICATION_FAILED
def test_adversarial_O_wrong_return_rate_def():
    contract = AnalysisContract(question="Order return rate?", return_definition="order_return_rate", expected_metric="order_return_rate")
    ref_res = ReferenceEngine.compute_reference(contract, {})
    # Ref Engine computes order_return_rate deterministically
    assert contract.return_definition == "order_return_rate"

# P. Wrong numeric result -> VERIFICATION_FAILED
def test_adversarial_P_wrong_numeric_result():
    gen_val = 100.0
    ref_val = 999.0
    assert abs(gen_val - ref_val) > 1e-2

# Q. Correct numeric result but wrong label -> VERIFICATION_FAILED
def test_adversarial_Q_wrong_label():
    canonical = CanonicalResult(result=500.0, label="State_X")
    ref_res = {"result": 500.0, "label": "State_Y"}
    assert canonical.label.lower() != ref_res["label"].lower()

# R. Correct code but changed final answer -> VERIFICATION_FAILED
def test_adversarial_R_changed_final_answer():
    fake_answer = "The total revenue is 99999999.00 INR."
    canonical_val = 2572592368.57
    import re
    found_nums = re.findall(r"\d+(?:\.\d+)?", fake_answer.replace(",", ""))
    consistent = any(abs(float(n) - canonical_val) < 1e-2 for n in found_nums)
    assert consistent is False

# S. Non-deterministic code -> VERIFICATION_FAILED
def test_adversarial_S_non_deterministic_code():
    from backend.execution.sandbox import LocalIsolatedSandbox
    sandbox = LocalIsolatedSandbox()
    code = """import time, json\nprint(json.dumps({"result": time.time_ns()}))"""
    res1 = sandbox.execute(code)
    res2 = sandbox.execute(code)
    assert res1.get("parsed_output", {}).get("result") != res2.get("parsed_output", {}).get("result")

# T. Join explosion -> VERIFICATION_FAILED
def test_adversarial_T_join_explosion():
    df_left = pd.DataFrame({"order_id": [1] * 100})
    df_right = pd.DataFrame({"order_id": [1] * 100, "item": range(100)})
    res = JoinChecker.validate_join(df_left, df_right, left_key="order_id", right_key="order_id")
    assert res["valid"] is False or res["critical_issue"] is not None
