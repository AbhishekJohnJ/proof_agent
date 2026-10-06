import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, Any

class CSVLoader:
    """Loads CSV files into Pandas DataFrame with error handling and metadata extraction."""

    @staticmethod
    def load(file_path: Path) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.stat().st_size == 0:
            raise ValueError("CSV file is empty (0 bytes).")

        try:
            # Try loading CSV with default pandas settings
            df = pd.read_csv(file_path)
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file contains no data.")
        except pd.errors.ParserError as e:
            raise ValueError(f"Malformed CSV file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to load CSV file: {str(e)}")

        if df.empty:
            raise ValueError("CSV contains empty dataset (0 rows or 0 columns).")

        metadata = {
            "filename": file_path.name,
            "file_type": "csv",
            "rows": len(df),
            "columns": len(df.columns),
            "file_size_bytes": file_path.stat().st_size,
            "column_names": list(df.columns),
            "status": "success"
        }

        return df, metadata
