from typing import Any, Dict, List
from backend.providers.base import CodeGenerationProvider

class MockCodeGenerationProvider(CodeGenerationProvider):
    """Mock Code Generation Provider generating valid Pandas code referencing controlled dataset workspace paths."""

    def generate_code(self, question: str, dataset_schemas: List[Dict[str, Any]], quality_warnings: List[Dict[str, Any]]) -> Dict[str, Any]:
        q_lower = question.lower()
        
        ds_id = dataset_schemas[0].get("dataset_id", "ds_default") if dataset_schemas else "ds_default"
        file_type = dataset_schemas[0].get("file_type", "csv") if dataset_schemas else "csv"
        
        rel_path = f"data/{ds_id}/data.{file_type}"

        if "revenue" in q_lower or "sales" in q_lower or "total" in q_lower:
            code = f"""import pandas as pd
import json

df = pd.read_csv("{rel_path}")
# Deduplicate if duplicate rows exist
df = df.drop_duplicates()
rev_col = [c for c in df.columns if 'revenue' in c.lower() or 'amount' in c.lower()][0]
total_rev = float(df[rev_col].dropna().sum())
print(json.dumps({{"result": total_rev, "metric": "total_revenue", "unit": "USD"}}))
"""
        elif "count" in q_lower or "rows" in q_lower or "customers" in q_lower:
            code = f"""import pandas as pd
import json

df = pd.read_csv("{rel_path}")
cnt = int(len(df))
print(json.dumps({{"result": cnt, "metric": "row_count", "unit": "count"}}))
"""
        else:
            code = f"""import pandas as pd
import json

df = pd.read_csv("{rel_path}")
df = df.drop_duplicates()
res = float(len(df))
print(json.dumps({{"result": res, "metric": "record_count", "unit": "count"}}))
"""

        return {
            "code": code,
            "explanation": "[MOCK CODE GENERATOR] Generated Pandas code using controlled workspace dataset path.",
            "expected_result_type": "number",
            "datasets_used": [ds_id]
        }
