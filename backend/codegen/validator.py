import ast
from typing import Tuple, List

ALLOWED_IMPORTS = {
    "pandas", "pd", "numpy", "np", "json", "math", "datetime", "re", "statistics"
}

FORBIDDEN_IMPORTS = {
    "os", "subprocess", "sys", "shutil", "socket", "http", "urllib",
    "requests", "httpx", "aiohttp", "ftplib", "builtins", "importlib",
    "ctypes", "multiprocessing", "threading", "pathlib", "glob", "pickle", "marshal"
}

FORBIDDEN_FUNCTIONS = {
    "eval", "exec", "compile", "__import__", "open", "input",
    "globals", "locals", "getattr", "setattr", "delattr"
}

class StaticCodeValidator:
    """AST-based static code validator enforcing an import allowlist and blocking dangerous builtins."""

    @classmethod
    def validate(cls, code_str: str) -> Tuple[bool, List[str]]:
        errors: List[str] = []

        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            return False, [f"Syntax error in generated code: {str(e)}"]

        for node in ast.walk(tree):
            # 1. Validate Import statements
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_name = alias.name.split(".")[0]
                    if root_name in FORBIDDEN_IMPORTS or root_name not in ALLOWED_IMPORTS:
                        errors.append(f"Forbidden import '{alias.name}' detected. Only {sorted(list(ALLOWED_IMPORTS))} are allowed.")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_name = node.module.split(".")[0]
                    if root_name in FORBIDDEN_IMPORTS or root_name not in ALLOWED_IMPORTS:
                        errors.append(f"Forbidden import from '{node.module}' detected. Only {sorted(list(ALLOWED_IMPORTS))} are allowed.")

            # 2. Validate Function & Attribute Calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in FORBIDDEN_FUNCTIONS:
                        errors.append(f"Forbidden call to dangerous function '{node.func.id}()'.")
                elif isinstance(node.func, ast.Attribute):
                    attr_name = node.func.attr
                    if attr_name in ["system", "popen", "spawn", "exec", "eval", "rmtree", "unlink", "remove", "rmdir"]:
                        errors.append(f"Forbidden method call '.{attr_name}()' detected.")

        is_valid = len(errors) == 0
        return is_valid, errors
