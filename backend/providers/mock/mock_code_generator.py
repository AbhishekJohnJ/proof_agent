from typing import Any, Dict, List
from backend.providers.base import CodeGenerationProvider
from backend.codegen.contract_code_gen import ContractCodeGenerator
from backend.models.analysis_contract import AnalysisContract

class MockCodeGenerationProvider(CodeGenerationProvider):
    """Mock Code Generation Provider producing contract-driven Pandas code without hardcoded keyword trees."""

    def generate_code(
        self,
        question: str,
        dataset_schemas: List[Dict[str, Any]],
        quality_warnings: List[Dict[str, Any]],
        analysis_contract: Any = None
    ) -> Dict[str, Any]:
        
        if analysis_contract and isinstance(analysis_contract, AnalysisContract):
            contract = analysis_contract
        elif analysis_contract and isinstance(analysis_contract, dict):
            contract = AnalysisContract(**analysis_contract)
        else:
            # Construct simple default contract if none provided
            req_ds = [s.get("dataset_id") for s in dataset_schemas if s.get("dataset_id")] if dataset_schemas else ["ds_orders"]
            contract = AnalysisContract(
                question=question,
                datasets_required=req_ds,
                columns_required=["final_amount"],
                expected_metric="total_revenue",
                expected_unit="INR"
            )

        return ContractCodeGenerator.generate_python_code(contract, dataset_schemas)
