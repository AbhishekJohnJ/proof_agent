import pandas as pd
from typing import Dict, Any

class SchemaExtractor:
    """Extracts tabular column schema and types deterministically."""

    @staticmethod
    def extract_schema(df: pd.DataFrame) -> Dict[str, Any]:
        schema = {}
        for col in df.columns:
            dtype_str = str(df[col].dtype)
            schema[str(col)] = {
                "dtype": dtype_str,
                "nullable": bool(df[col].isnull().any()),
                "sample": df[col].dropna().head(3).tolist()
            }
        return schema
