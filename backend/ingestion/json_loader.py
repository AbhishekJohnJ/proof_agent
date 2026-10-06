import json
import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, Any

class JSONLoader:
    """Loads JSON files (records or dicts) into Pandas DataFrame."""

    @staticmethod
    def load(file_path: Path) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.stat().st_size == 0:
            raise ValueError("JSON file is empty (0 bytes).")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                # If dict of lists or single record
                df = pd.DataFrame([data]) if not any(isinstance(v, list) for v in data.values()) else pd.DataFrame(data)
            else:
                raise ValueError("Unsupported JSON root structure (must be list or dict).")
        except json.JSONDecodeError as e:
            raise ValueError(f"Malformed JSON file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to load JSON file: {str(e)}")

        if df.empty:
            raise ValueError("JSON dataset contains no tabular data (0 rows or 0 columns).")

        metadata = {
            "filename": file_path.name,
            "file_type": "json",
            "rows": len(df),
            "columns": len(df.columns),
            "file_size_bytes": file_path.stat().st_size,
            "column_names": list(df.columns),
            "status": "success"
        }

        return df, metadata
