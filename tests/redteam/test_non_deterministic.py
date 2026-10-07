import pytest
from backend.execution.sandbox import LocalIsolatedSandbox
from backend.verification.reproducibility import ReproducibilityVerifier

def test_nondeterministic_random_code_fails_reproducibility():
    sandbox = LocalIsolatedSandbox()

    nondet_code = """import random
import json

val = random.randint(1, 1000000)
print(json.dumps({"result": val}))
"""

    exec_res = sandbox.execute(nondet_code)
    status, diff, method, errors = ReproducibilityVerifier.verify_reproducibility(
        sandbox, nondet_code, exec_res, []
    )

    assert status.value == "FAIL"
    assert len(errors) > 0 and ("mismatch" in errors[0].lower() or "reproducibility" in errors[0].lower())
