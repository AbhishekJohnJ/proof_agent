import ast
from typing import Tuple, List

DANGEROUS_IMPORTS = {
    "os", "subprocess", "sys", "shutil", "socket", "http", "urllib",
    "requests", "httpx", "aiohttp", "ftplib", "builtins", "importlib",
    "ctypes", "multiprocessing", "threading"
}

DANGEROUS_FUNCTIONS = {
    "eval", "exec", "compile", "__import__", "open", "input", "globals", "locals"
}

class StaticCodeValidator:
    """Static Code Validator inspecting Python AST for security violations prior to execution."""

    @classmethod
    def validate(cls, code_str: str) -> Tuple[bool, List[str]]:
        errors: List[str] = []

        try:
            tree = ast.parse(code_str)
        except SyntaxError as e:
            return False, [f"Syntax error in generated code: {str(e)}"]

        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_name = alias.name.split(".")[0]
                    if root_name in DANGEROUS_IMPORTS:
                        errors.append(f"Forbidden import '{alias.name}' detected.")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_name = node.module.split(".")[0]
                    if root_name in DANGEROUS_IMPORTS:
                        errors.append(f"Forbidden import from '{node.module}' detected.")

            # Check function calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in DANGEROUS_FUNCTIONS:
                        errors.append(f"Forbidden call to dangerous function '{node.func.id}()'.")
                elif isinstance(node.func, ast.Attribute):
                    attr_name = node.func.attr
                    if attr_name in ["system", "popen", "spawn", "exec", "eval", "rmtree"]:
                        errors.append(f"Forbidden method call '.{attr_name}()' detected.")

        is_valid = len(errors) == 0
        return is_valid, errors
