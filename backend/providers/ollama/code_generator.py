import json
import re
import time
from typing import Dict, Any, List, Optional
from backend.providers.base import CodeGenerationProvider
from backend.providers.ollama.client import OllamaClient
from backend.providers.ollama.config import ollama_config
from backend.codegen.contract_code_gen import ContractCodeGenerator
from backend.codegen.validator import StaticCodeValidator
from backend.models.analysis_contract import AnalysisContract

class OllamaCodeGenerator(CodeGenerationProvider):
    """
    Production Code Generator backed by local DeepSeek Coder model via Ollama.
    Converts a validated AnalysisContract into executable, sandboxed Pandas analysis Python code.
    """

    SYSTEM_PROMPT = """You are DeepSeek-Coder, the Lead Data Analytics Code Generator for ProofAI.
Your task is to write clean, deterministic Python pandas code based on a validated AnalysisContract.

STRICT SECURITY & EXECUTION CONSTRAINTS:
1. Use ONLY pandas and numpy libraries.
2. Load datasets strictly using relative path: `pd.read_csv("data/<dataset_id>/data.csv")`.
3. DO NOT access system os/subprocess, network, external files, or secrets.
4. DO NOT use eval, exec, or arbitrary dynamic imports.
5. The final answer MUST be printed as a single JSON string using `print(json.dumps({"result": <numerical_value_or_string>, "metric": "<metric_name>", "unit": "<unit_string>"}))`.
6. DO NOT write explanations or conversational text outside the JSON code response.

JSON RESPONSE FORMAT:
{
    "code": "import pandas as pd\\nimport json\\n...",
    "explanation": "Pandas code calculating metrics based on contract."
}
"""

    def __init__(self, model_name: Optional[str] = None, client: Optional[OllamaClient] = None):
        self.model_name = model_name or ollama_config.code_model
        self.client = client or OllamaClient()

    def _extract_code_from_response(self, response_text: str) -> str:
        text = response_text.strip()
        # Check if response is JSON with a 'code' field
        if text.startswith("{") and "code" in text:
            try:
                data = json.loads(text)
                if "code" in data and data["code"]:
                    return data["code"]
            except Exception:
                pass

        # Check for python markdown code blocks
        if "```python" in text:
            match = re.search(r"```python\s*(.*?)\s*```", text, re.DOTALL)
            if match:
                return match.group(1).strip()

        if "```" in text:
            match = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
            if match:
                return match.group(1).strip()

        return text

    def generate_code(
        self,
        question: str,
        dataset_schemas: List[Dict[str, Any]],
        quality_warnings: List[Dict[str, Any]],
        analysis_contract: Any = None
    ) -> Dict[str, Any]:
        start_time = time.perf_counter()

        # Parse AnalysisContract
        contract = None
        if analysis_contract:
            if isinstance(analysis_contract, AnalysisContract):
                contract = analysis_contract
            elif isinstance(analysis_contract, dict):
                try:
                    contract = AnalysisContract(**analysis_contract)
                except Exception:
                    contract = None

        contract_json = contract.model_dump_json() if contract else "{}"

        prompt = (
            f"USER QUESTION: {question}\n\n"
            f"VALIDATED ANALYSIS CONTRACT:\n{contract_json}\n\n"
            f"DATASET SCHEMAS:\n{json.dumps(dataset_schemas, indent=2)}\n\n"
            "Generate executable Python code for this contract:"
        )

        try:
            res = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                json_format=True,
                temperature=0.0
            )
            raw_output = res.get("response", "")
            extracted_code = self._extract_code_from_response(raw_output)
            latency_ms = int((time.perf_counter() - start_time) * 1000)

            # Static security check
            is_valid, validation_errors = StaticCodeValidator.validate(extracted_code)

            if is_valid and "import pandas" in extracted_code and "json.dumps" in extracted_code:
                return {
                    "code": extracted_code,
                    "explanation": f"[DEEPSEEK-CODER] Generated Python script via local Ollama ({self.model_name}).",
                    "expected_result_type": (contract.expected_result_type if contract else "scalar"),
                    "datasets_used": (contract.datasets_required if contract else []),
                    "_provenance": {
                        "provider": "ollama",
                        "model": self.model_name,
                        "latency_ms": res.get("latency_ms", latency_ms)
                    }
                }
        except Exception:
            pass

        # Fall back to contract-driven deterministic code generator if model output fails security or syntax validation
        if contract:
            det_res = ContractCodeGenerator.generate_python_code(contract, dataset_schemas)
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            det_res["_provenance"] = {
                "provider": "ollama",
                "model": self.model_name,
                "latency_ms": latency_ms,
                "fallback_to_contract_generator": True
            }
            return det_res

        # If no contract and model fails
        return {
            "code": "# CODE GENERATION FAILED\nprint('{\"result\": null, \"error\": \"DeepSeek model failed to generate valid code\"}')",
            "explanation": "DeepSeek code generation failed static security check.",
            "expected_result_type": "refusal",
            "datasets_used": []
        }
