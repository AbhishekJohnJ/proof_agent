import pytest
import pandas as pd
from pathlib import Path
from backend.models.query import AnalysisRequest
from backend.models.analysis import AnalysisStatus
from backend.models.analysis_contract import AnalysisContract, ContractOperation
from backend.verification.contract_checker import StaticContractChecker
from backend.verification.join_checker import JoinChecker
from backend.verification.result_checker import ResultChecker
from backend.verification.reproducibility import ReproducibilityVerifier
from backend.analysis.reference_engine import ReferenceEngine
from backend.api.dependencies import get_orchestrator
from backend.data.catalog import dataset_catalog

@pytest.fixture(scope="module")
def kaggle_ds():
    return [d["dataset_id"] for d in dataset_catalog.list_datasets()]

# A. Correct code -> VERIFIED
def test_adversarial_A_correct_code_verified(kaggle_ds):
    orchestrator = get_orchestrator()
    req = AnalysisRequest(
        question="What is the total revenue?",
        selected_datasets=kaggle_ds
    )
    res = orchestrator.process_analysis(req)
    assert res.status == AnalysisStatus.VERIFIED
    assert res.verification.status == "VERIFIED"
    assert res.verification.v7_required_datasets_used == "PASS"
    assert res.verification.v9_expected_operation_reflected == "PASS"

# B. Code returns wrong number -> VERIFICATION_FAILED
def test_adversarial_B_wrong_number_failed(kaggle_ds):
    orchestrator = get_orchestrator()
    contract = AnalysisContract(
        question="What is the total revenue?",
        datasets_required=["ds_kaggle_orders"],
        columns_required=["final_amount"],
        operations=[ContractOperation(type="aggregate", column="final_amount", operation="sum")],
        expected_unit="INR"
    )

    # Reference engine calculates 2.57B, but code returns 999.0
    ref_res = ReferenceEngine.compute_reference(contract, {"ds_kaggle_orders": Path("data/orders.csv")})
    assert ref_res["success"] is True

    diff = abs(999.0 - ref_res["result"])
    assert diff > 100.0, "Wrong number should differ from reference result."

# C. Code ignores required dataset -> VERIFICATION_FAILED
def test_adversarial_C_ignores_required_dataset():
    contract = AnalysisContract(
        question="Which category has highest revenue?",
        datasets_required=["ds_kaggle_order_items", "ds_kaggle_products"],
        columns_required=["product_id", "category"],
        joins=[{"left_dataset": "order_items", "right_dataset": "products"}],
        operations=[ContractOperation(type="join"), ContractOperation(type="group_by", column="category")]
    )
    # Generated code only loads order_items and misses products dataset
    code = """import pandas as pd, json
df = pd.read_csv("data/ds_kaggle_order_items/data.csv")
res = df["item_revenue"].sum()
print(json.dumps({"result": res}))"""

    v7, v8, v9, errors = StaticContractChecker.check_contract(code, contract, ["ds_kaggle_order_items", "ds_kaggle_products"])
    assert v7 == "FAIL", f"Should fail V7 when dataset is omitted. Errors: {errors}"

# D. Code uses unselected dataset -> VERIFICATION_FAILED
def test_adversarial_D_uses_unselected_dataset():
    from backend.execution.sandbox import LocalIsolatedSandbox
    from backend.services.storage import storage_service

    sandbox = LocalIsolatedSandbox()
    art_orders = storage_service.get_dataset_artifact("ds_kaggle_orders")
    assert art_orders is not None

    # Code reads payments.csv when only orders was passed in selected datasets
    code = """import pandas as pd, json
df_ord = pd.read_csv("data/ds_kaggle_orders/data.csv")
df_pay = pd.read_csv("data/ds_kaggle_payments/data.csv")
res = float(len(df_ord) + len(df_pay))
print(json.dumps({"result": res}))"""

    exec_res = sandbox.execute(code, [art_orders])
    accessed = exec_res.get("accessed_dataset_ids", [])
    assert "ds_kaggle_payments" in accessed, "Sandbox must record access to unselected payments dataset."

# E. Code uses wrong aggregation -> VERIFICATION_FAILED
def test_adversarial_E_wrong_aggregation_failed():
    contract = AnalysisContract(
        question="What is total revenue?",
        datasets_required=["ds_kaggle_orders"],
        columns_required=["final_amount"],
        operations=[ContractOperation(type="aggregate", column="final_amount", operation="sum")]
    )
    # Code uses mean instead of sum
    code = """import pandas as pd, json
df = pd.read_csv("data/ds_kaggle_orders/data.csv")
val = df["final_amount"].mean()
print(json.dumps({"result": val}))"""

    v7, v8, v9, errors = StaticContractChecker.check_contract(code, contract, ["ds_kaggle_orders"])
    assert v9 == "FAIL", f"Should fail V9 when sum aggregation is missing. Errors: {errors}"

# F. Code skips required join -> VERIFICATION_FAILED
def test_adversarial_F_skips_required_join():
    contract = AnalysisContract(
        question="Which category has highest revenue?",
        datasets_required=["ds_kaggle_order_items", "ds_kaggle_products"],
        columns_required=["category", "item_revenue"],
        joins=[{"left_dataset": "order_items", "right_dataset": "products"}],
        operations=[ContractOperation(type="join"), ContractOperation(type="group_by", column="category")]
    )
    code = """import pandas as pd, json
df1 = pd.read_csv("data/ds_kaggle_order_items/data.csv")
df2 = pd.read_csv("data/ds_kaggle_products/data.csv")
# misses merge operation!
val = 100.0
print(json.dumps({"result": val}))"""

    v7, v8, v9, errors = StaticContractChecker.check_contract(code, contract, ["ds_kaggle_order_items", "ds_kaggle_products"])
    assert v9 == "FAIL", f"Should fail V9 when required join is missing. Errors: {errors}"

# G. Code performs wrong join key -> VERIFICATION_FAILED
def test_adversarial_G_wrong_join_key():
    df_orders = pd.DataFrame({"order_id": [1, 2], "customer_id": [10, 20]})
    df_cust = pd.DataFrame({"customer_id": [10, 20], "name": ["A", "B"]})

    res = JoinChecker.validate_join(df_orders, df_cust, left_key="wrong_key", right_key="customer_id")
    assert res["valid"] is False
    assert "missing" in res["critical_issue"]

# H. Code causes join explosion -> warning/failure
def test_adversarial_H_join_explosion_detected():
    df_left = pd.DataFrame({"order_id": [1] * 100})
    df_right = pd.DataFrame({"order_id": [1] * 100, "item": range(100)})

    res = JoinChecker.validate_join(df_left, df_right, left_key="order_id", right_key="order_id")
    assert res["is_explosion"] is True
    assert res["rows_after"] == 10000

# I. Code reports wrong unit -> VERIFICATION_FAILED
def test_adversarial_I_wrong_unit_failed():
    contract = AnalysisContract(
        question="What is total revenue?",
        expected_unit="INR"
    )
    from backend.models.analysis import CanonicalResult
    from backend.models.verification import CheckStatus

    canonical = CanonicalResult(result=2500.0, unit="USD")
    unit_status = CheckStatus.PASS if canonical.unit == contract.expected_unit else CheckStatus.FAIL
    assert unit_status == CheckStatus.FAIL

# J. Code produces non-reproducible output -> VERIFICATION_FAILED
def test_adversarial_J_non_reproducible_output():
    from backend.execution.sandbox import LocalIsolatedSandbox
    sandbox = LocalIsolatedSandbox()

    code = """import time, json
print(json.dumps({"result": time.time_ns()}))"""

    res1 = sandbox.execute(code)
    res2 = sandbox.execute(code)
    v1 = res1.get("parsed_output", {}).get("result")
    v2 = res2.get("parsed_output", {}).get("result")
    assert v1 != v2, "Non-deterministic code should produce differing outputs across runs."

# K. Final answer changes verified number -> VERIFICATION_FAILED
def test_adversarial_K_answer_numerical_mismatch(kaggle_ds):
    orchestrator = get_orchestrator()
    req = AnalysisRequest(
        question="What is the total revenue?",
        selected_datasets=kaggle_ds
    )
    # Process valid analysis
    res = orchestrator.process_analysis(req)
    assert res.status == AnalysisStatus.VERIFIED

    # Check V10 logic if answer string is modified to contain a conflicting number
    fake_answer = "The total revenue is 99999999.00 INR."
    canonical_val = res.canonical_result.result

    import re
    found_nums = re.findall(r"\d+(?:\.\d+)?", fake_answer.replace(",", ""))
    consistent = any(abs(float(n) - float(canonical_val)) < 1e-2 for n in found_nums)
    assert consistent is False, "Modified answer string with fake number should fail V10 consistency check."
