from backend.codegen.validator import StaticCodeValidator

def test_safe_code_passes_validation():
    safe_code = """import pandas as pd
import json

df = pd.read_csv("sales.csv")
res = float(df["revenue"].sum())
print(json.dumps({"result": res}))
"""
    is_valid, errors = StaticCodeValidator.validate(safe_code)
    assert is_valid is True
    assert len(errors) == 0

def test_dangerous_os_system_rejected():
    dangerous_code = """import os
os.system("rm -rf /")
"""
    is_valid, errors = StaticCodeValidator.validate(dangerous_code)
    assert is_valid is False
    assert any("Forbidden import 'os'" in e for e in errors)

def test_subprocess_rejected():
    dangerous_code = """import subprocess
subprocess.run(["ls"])
"""
    is_valid, errors = StaticCodeValidator.validate(dangerous_code)
    assert is_valid is False
