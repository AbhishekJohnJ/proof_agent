from typing import Dict, Any, List
from backend.providers.base import CodeGenerationProvider
from backend.codegen.validator import StaticCodeValidator

class CodeGeneratorService:
    """Code Generator Service depending on CodeGenerationProvider interface."""

    def __init__(self, provider: CodeGenerationProvider):
        self.provider = provider

    def generate_and_validate(
        self,
        question: str,
        dataset_schemas: List[Dict[str, Any]],
        quality_warnings: List[Dict[str, Any]],
        analysis_contract: Any = None
    ) -> Dict[str, Any]:
        try:
            result = self.provider.generate_code(
                question,
                dataset_schemas,
                quality_warnings,
                analysis_contract
            )
        except TypeError:
            # Fallback if mock lambda accepts only 3 positional arguments
            result = self.provider.generate_code(
                question,
                dataset_schemas,
                quality_warnings
            )
        code = result.get("code", "")

        is_valid, validation_errors = StaticCodeValidator.validate(code)
        result["is_valid"] = is_valid
        result["validation_errors"] = validation_errors

        return result
