from backend.execution.runner import LocalCodeRunner

def test_code_runner_executes_valid_code():
    code = """import json
res = 42 * 10
print(json.dumps({"result": res, "metric": "test"}))
"""
    res = LocalCodeRunner.run_code(code)
    assert res["success"] is True
    assert res["parsed_output"]["result"] == 420

def test_code_runner_handles_runtime_error():
    code = """x = 1 / 0"""
    res = LocalCodeRunner.run_code(code)
    assert res["success"] is False
    assert "ZeroDivisionError" in res["stderr"]
