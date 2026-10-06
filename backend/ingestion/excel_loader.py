import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, Any

class ExcelLoader:
    """Loads Excel (.xlsx, .xls) files into Pandas DataFrame."""

    @staticmethod
    def load(file_path: Path, sheet_name: int | str = 0) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.stat().st_size == 0:
            raise ValueError("Excel file is empty (0 bytes).")

        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        except Exception as e:
            raise ValueError(f"Invalid or corrupted Excel file: {str(e)}")

        if df.empty:
            raise ValueError("Excel file contains empty sheet (0 rows or 0 columns).")

        metadata = {
            "filename": file_path.name,
            "file_type": "excel",
            "rows": len(df),
            "columns": len(df.columns),
            "file_size_bytes": file_path.stat().st_size,
            "column_names": list(df.columns),
            "status": "success"
        }

        return df, metadata
