import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.storage import storage_service
from backend.services.upload_security import SafeUploadHandler

client = TestClient(app)

def test_identical_bytes_duplicate_handling(tmp_path):
    import time
    csv_bytes = f"order_id,product,revenue\n999,FreshProduct_{time.time()},9999.0\n".encode("utf-8")
    
    res1 = client.post("/upload", files={"file": ("sales_a.csv", csv_bytes, "text/csv")})
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["is_duplicate_content"] is False
    up1 = data1["upload_id"]
    ds1 = data1["dataset_id"]
    hash1 = data1["raw_sha256"]

    res2 = client.post("/upload", files={"file": ("sales_b.csv", csv_bytes, "text/csv")})
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["is_duplicate_content"] is True
    up2 = data2["upload_id"]
    ds2 = data2["dataset_id"]
    hash2 = data2["raw_sha256"]

    assert up1 != up2
    assert ds1 == ds2
    assert hash1 == hash2


def test_same_filename_different_bytes():
    csv_bytes1 = b"order_id,product,revenue\n101,Laptop,1200.0\n"
    csv_bytes2 = b"order_id,product,revenue\n101,Laptop,1500.0\n"

    res1 = client.post("/upload", files={"file": ("orders.csv", csv_bytes1, "text/csv")})
    res2 = client.post("/upload", files={"file": ("orders.csv", csv_bytes2, "text/csv")})

    assert res1.status_code == 200
    assert res2.status_code == 200

    data1 = res1.json()
    data2 = res2.json()

    assert data1["dataset_id"] != data2["dataset_id"]
    assert data1["raw_sha256"] != data2["raw_sha256"]

def test_one_byte_difference():
    csv1 = b"student_id,marks\n1,90\n"
    csv2 = b"student_id,marks\n1,91\n"

    res1 = client.post("/upload", files={"file": ("marks.csv", csv1, "text/csv")})
    res2 = client.post("/upload", files={"file": ("marks.csv", csv2, "text/csv")})

    assert res1.json()["dataset_id"] != res2.json()["dataset_id"]

def test_empty_file_rejected():
    res = client.post("/upload", files={"file": ("empty.csv", b"", "text/csv")})
    assert res.status_code == 400
    assert "empty" in res.json()["detail"].lower()
