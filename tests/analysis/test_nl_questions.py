import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.storage import storage_service
from backend.models.analysis import AnalysisStatus

client = TestClient(app)

def test_nl_total_revenue_query(tmp_path):
    csv_content = b"order_id,product,revenue\nO1,Laptop,1000\nO2,Phone,500\nO3,Tablet,300\n"
    res_up = client.post("/upload", files={"file": ("custom_revenue.csv", csv_content, "text/csv")})
    assert res_up.status_code == 200
    ds_id = res_up.json()["dataset_id"]

    res_an = client.post("/analysis", json={
        "question": "What is the total revenue?",
        "selected_datasets": [ds_id]
    })
    assert res_an.status_code == 200
    data = res_an.json()
    assert data["status"] in ["VERIFIED", "VERIFICATION_FAILED", "MODEL_NOT_CONFIGURED"]
    if data["status"] == "VERIFIED":
        assert "1800" in data["answer"] or "1800.0" in str(data.get("canonical_result", {}))

def test_nl_invalid_column_query_refusal(tmp_path):
    csv_content = b"student_id,branch,marks\nS1,CS,90\nS2,ECE,85\n"
    res_up = client.post("/upload", files={"file": ("custom_students.csv", csv_content, "text/csv")})
    ds_id = res_up.json()["dataset_id"]

    res_an = client.post("/analysis", json={
        "question": "What is the average of non_existent_column_xyz?",
        "selected_datasets": [ds_id]
    })
    assert res_an.status_code == 200
    data = res_an.json()
    assert data["status"] in ["REFUSED", "VERIFICATION_FAILED"]
