from backend.verification.result_checker import ResultChecker
from backend.verification.reproducibility import ReproducibilityVerifier
from backend.execution.sandbox import LocalIsolatedSandbox
from backend.models.verification import CheckStatus

def test_result_checker_valid():
    exec_res = {
        "success": True,
        "stdout": '{"result": 100.0}',
        "parsed_output": {"result": 100.0}
    }
    out_present, out_valid, type_matched, errors = ResultChecker.check_result(exec_res, "number")
    assert out_present == CheckStatus.PASS
    assert out_valid == CheckStatus.PASS
    assert type_matched == CheckStatus.PASS
    assert len(errors) == 0

def test_reproducibility_verifier():
    sandbox = LocalIsolatedSandbox()
    code = """import json\nprint(json.dumps({"result": 50}))"""
    initial_res = sandbox.execute(code)
    status, diff, method, errors = ReproducibilityVerifier.verify_reproducibility(sandbox, code, initial_res, [])
    assert status == CheckStatus.PASS
    assert len(errors) == 0

def test_dataset_resolver_strict_no_fuzzy_matching():
    import pytest
    from backend.data.dataset_resolver import DatasetResolver, DatasetResolverError
    from backend.analysis.contract_executor import ContractExecutor
    from backend.models.analysis_contract import AnalysisContract

    # 1. DatasetResolver fails when ds_A does not exist
    with pytest.raises(DatasetResolverError):
        DatasetResolver.resolve_dataset("ds_A")

    # 2. ContractExecutor must NOT use ds_A_backup when contract requests ds_A
    contract = AnalysisContract(
        question="Test strict resolution",
        datasets_required=["ds_A"],
        columns_required=["amount"]
    )
    dataset_files = {
        "ds_A_backup": "tests/fixtures/clean_sales.csv"
    }
    result = ContractExecutor.execute(contract, dataset_files)
    assert result["success"] is False
    assert "ds_A" in result["error"]
