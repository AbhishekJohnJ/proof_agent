import pytest

pytestmark = pytest.mark.redteam
from backend.codegen.validator import StaticCodeValidator

def test_malicious_security_escapes_fail_ast_validation():
    malicious_scripts = [
        "import os\nos.system('rm -rf /')",
        "import subprocess\nsubprocess.run(['ls', '-la'])",
        "import socket\ns = socket.socket()",
        "import sys\nsys.exit(0)",
        "eval('__import__(\"os\").system(\"whoami\")')"
    ]

    for script in malicious_scripts:
        is_valid, errors = StaticCodeValidator.validate(script)
        assert not is_valid, f"Script '{script}' should have failed AST security validation"
        assert len(errors) > 0
