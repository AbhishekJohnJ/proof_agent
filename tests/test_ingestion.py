import pytest
from pathlib import Path
from backend.ingestion.csv_loader import CSVLoader
from backend.ingestion.json_loader import JSONLoader
from backend.ingestion.file_manager import FileManager

def test_csv_ingestion_valid():
    sample_path = Path("datasets/sample/sales.csv")
    df, meta = CSVLoader.load(sample_path)
    assert len(df) > 0
    assert "revenue" in df.columns
    assert meta["file_type"] == "csv"

def test_csv_ingestion_invalid_file():
    with pytest.raises(FileNotFoundError):
        CSVLoader.load(Path("non_existent.csv"))

def test_file_manager_ingestion():
    sample_path = Path("datasets/sample/customers.csv")
    df, meta = FileManager.ingest_dataset(sample_path)
    assert meta.filename == "customers.csv"
    assert meta.rows > 0
    assert meta.status == "success"

def test_unsupported_format_rejection():
    with pytest.raises(ValueError, match="Unsupported file format"):
        FileManager.ingest_dataset(Path("test.unsupported"))
