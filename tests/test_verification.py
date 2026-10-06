from backend.verification.result_checker import ResultChecker
from backend.verification.reproducibility import ReproducibilityVerifier
from backend.execution.sandbox import LocalIsolatedSandbox

def test_result_checker_valid():
    exec_res = {
        "success": True,
        "stdout": '{"result": 100.0}',
        "parsed_output": {"result": 100.0}
    }
    out_present, out_valid, errors = ResultChecker.check_result(exec_res, "number")
    assert out_present is True
    assert out_valid is True
    assert len(errors) == 0

def test_reproducibility_verifier():
    sandbox = LocalIsolatedSandbox()
    code = """import json\nprint(json.dumps({"result": 50}))"""
    initial_res = sandbox.execute(code)
    repro, errors = ReproducibilityVerifier.verify_reproducibility(sandbox, code, initial_res)
    assert repro is True
    assert len(errors) == 0
