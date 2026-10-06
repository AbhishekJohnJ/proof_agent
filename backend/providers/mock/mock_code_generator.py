from typing import Any, Dict, List
from backend.providers.base import CodeGenerationProvider

class MockCodeGenerationProvider(CodeGenerationProvider):
    """Mock Code Generation Provider returning valid executable Pandas python code snippets for dev/testing."""

    def generate_code(self, question: str, dataset_schemas: List[Dict[str, Any]], quality_warnings: List[Dict[str, Any]]) -> Dict[str, Any]:
        q_lower = question.lower()
        
        # Determine dataset name if available
        first_dataset = dataset_schemas[0].get("filename", "data.csv") if dataset_schemas else "data.csv"

        if "revenue" in q_lower or "total" in q_lower or "sum" in q_lower:
            code = f"""import pandas as pd
import json

df = pd.read_csv("{first_dataset}")
# Handle missing revenue if any
revenue_col = [c for c in df.columns if 'revenue' in c.lower() or 'amount' in c.lower()][0]
total_revenue = float(df[revenue_col].dropna().sum())
print(json.dumps({{"result": total_revenue, "metric": "total_revenue"}}))
"""
        elif "count" in q_lower or "rows" in q_lower:
            code = f"""import pandas as pd
import json

df = pd.read_csv("{first_dataset}")
row_count = int(len(df))
print(json.dumps({{"result": row_count, "metric": "row_count"}}))
"""
        else:
            code = f"""import pandas as pd
import json

df = pd.read_csv("{first_dataset}")
result_val = float(len(df))
print(json.dumps({{"result": result_val, "metric": "generic_count"}}))
"""

        return {
            "code": code,
            "explanation": "[MOCK CODE GENERATOR] Deterministic executable python script.",
            "expected_result_type": "number",
            "datasets_used": [first_dataset]
        }
