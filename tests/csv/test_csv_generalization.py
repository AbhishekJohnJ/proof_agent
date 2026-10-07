import pytest
from pathlib import Path
from backend.ingestion.file_manager import FileManager
from backend.profiling.profiler import DataProfiler

def test_sales_csv_ingestion(tmp_path):
    fpath = tmp_path / "sales.csv"
    fpath.write_bytes(b"order_id,product,category,revenue,state\nO1,Laptop,Tech,1200.0,Karnataka\nO2,Shirt,Apparel,40.0,Tamil Nadu\n")
    
    df, meta = FileManager.ingest_dataset(fpath)
    assert meta.rows == 2
    assert meta.columns == 5
    assert set(df.columns) == {"order_id", "product", "category", "revenue", "state"}
    profile = DataProfiler.profile("ds_sales", "sales.csv", df)
    assert profile.rows == 2

def test_students_csv_ingestion(tmp_path):
    fpath = tmp_path / "students.csv"
    fpath.write_bytes(b"student_id,branch,marks,attendance\nS1,CS,95,90\nS2,ECE,88,85\nS3,ME,75,92\n")

    df, meta = FileManager.ingest_dataset(fpath)
    assert meta.rows == 3
    assert "marks" in df.columns
    profile = DataProfiler.profile("ds_students", "students.csv", df)
    assert profile.columns == 4

def test_employees_csv_ingestion(tmp_path):
    fpath = tmp_path / "employees.csv"
    fpath.write_bytes(b"employee_id,department,salary,joining_date\nE101,Engineering,150000,2022-01-15\nE102,HR,80000,2021-06-01\n")

    df, meta = FileManager.ingest_dataset(fpath)
    assert meta.rows == 2
    assert "salary" in df.columns

def test_weird_headers_csv_ingestion(tmp_path):
    fpath = tmp_path / "weird_sales.csv"
    fpath.write_bytes(b"Customer Name,Revenue ($),Order Date\nAlice Smith,150.50,2025-03-01\nBob Jones,200.00,2025-03-02\n")

    df, meta = FileManager.ingest_dataset(fpath)
    assert meta.rows == 2
    assert "Customer Name" in df.columns
    assert "Revenue ($)" in df.columns
