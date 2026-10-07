import uuid
from pathlib import Path
from typing import Tuple, Dict, Any
import pandas as pd
from backend.ingestion.csv_loader import CSVLoader
from backend.ingestion.excel_loader import ExcelLoader
from backend.ingestion.json_loader import JSONLoader
from backend.models.dataset import DatasetMetadata

class FileManager:
    """Unified file manager that detects format and delegates to appropriate loader."""

    SUPPORTED_EXTENSIONS = {
        ".csv": CSVLoader,
        ".xlsx": ExcelLoader,
        ".xls": ExcelLoader,
        ".json": JSONLoader,
    }

    @classmethod
    def ingest_dataset(
        cls,
        file_path: Path,
        dataset_id: str | None = None,
        upload_id: str | None = None,
        raw_sha256: str | None = None
    ) -> Tuple[pd.DataFrame, DatasetMetadata]:
        ext = file_path.suffix.lower()
        if ext not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file format '{ext}'. Supported formats: {list(cls.SUPPORTED_EXTENSIONS.keys())}")

        loader = cls.SUPPORTED_EXTENSIONS[ext]
        df, meta_dict = loader.load(file_path)

        ds_id = dataset_id or f"ds_{uuid.uuid4().hex[:8]}"

        metadata = DatasetMetadata(
            dataset_id=ds_id,
            upload_id=upload_id,
            raw_sha256=raw_sha256,
            filename=file_path.name,
            file_type=ext.lstrip("."),
            rows=meta_dict["rows"],
            columns=meta_dict["columns"],
            file_size_bytes=meta_dict["file_size_bytes"],
            created_at=pd.Timestamp.now().isoformat(),
            status="success"
        )

        return df, metadata

