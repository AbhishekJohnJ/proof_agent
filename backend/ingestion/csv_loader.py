import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, Any, List

MISSING_VALUE_MARKERS = [
    "NaN", "NA", "N/A", "NULL", "null", "empty", "#N/A", "n/a", "None", "nan", "none"
]

ENCODING_CANDIDATES = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]

class CSVLoader:
    """Loads CSV files into Pandas DataFrame with multi-encoding fallback, delimiter auto-detection, error handling, and metadata extraction."""

    @staticmethod
    def load(file_path: Path) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.stat().st_size == 0:
            raise ValueError("CSV file is empty (0 bytes).")

        df: pd.DataFrame | None = None
        last_error: Exception | None = None

        # 1. Multi-encoding & Delimiter Fallback Loop
        for encoding in ENCODING_CANDIDATES:
            try:
                # Try auto-detecting delimiter first, or fallback to default engine
                try:
                    df = pd.read_csv(
                        file_path,
                        encoding=encoding,
                        na_values=MISSING_VALUE_MARKERS,
                        sep=None,
                        engine="python"
                    )
                except Exception:
                    df = pd.read_csv(
                        file_path,
                        encoding=encoding,
                        na_values=MISSING_VALUE_MARKERS
                    )
                if df is not None:
                    break
            except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError, ValueError) as ex:
                last_error = ex
                continue

        if df is None:
            raise ValueError(f"Failed to parse CSV file: {str(last_error or 'Unknown parsing failure')}")

        if df.empty or len(df.columns) == 0:
            raise ValueError("CSV contains empty dataset (0 rows or 0 columns).")

        metadata = {
            "filename": file_path.name,
            "file_type": "csv",
            "rows": len(df),
            "columns": len(df.columns),
            "file_size_bytes": file_path.stat().st_size,
            "column_names": [str(c) for c in df.columns],
            "status": "success"
        }

        return df, metadata

