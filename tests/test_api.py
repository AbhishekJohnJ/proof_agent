from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "model_providers" in data

def test_datasets_list_endpoint():
    response = client.get("/api/datasets")
    assert response.status_code == 200

def test_upload_file_endpoint():
    with open("datasets/sample/sales.csv", "rb") as f:
        response = client.post("/api/upload", files={"file": ("sales.csv", f, "text/csv")})
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "dataset"
    assert "metadata" in data

def test_analysis_query_endpoint():
    # First upload dataset
    with open("datasets/sample/sales.csv", "rb") as f:
        up_res = client.post("/api/upload", files={"file": ("sales.csv", f, "text/csv")})
    ds_id = up_res.json()["id"]

    query_payload = {
        "question": "What is the total revenue?",
        "selected_datasets": [ds_id]
    }
    response = client.post("/api/analysis/query", json=query_payload)
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert "verification" in data
