import os
from fastapi.testclient import TestClient

from banking_api.main import app

client = TestClient(app)

def setup_module():
    # Force the API to use the small test dataset
    os.environ["DATA_DIR"] = os.path.join("tests", "data")

def test_system_health():
    r = client.get("/api/system/health")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data

def test_transactions_list():
    r = client.get("/api/transactions?limit=2")
    assert r.status_code == 200
    data = r.json()
    assert "transactions" in data
    assert data["limit"] == 2

def test_transactions_types():
    r = client.get("/api/transactions/types")
    assert r.status_code == 200
    data = r.json()
    assert "types" in data
    assert len(data["types"]) > 0

def test_stats_overview():
    r = client.get("/api/stats/overview")
    assert r.status_code == 200
    data = r.json()
    assert "total_transactions" in data

def test_fraud_predict():
    payload = {"amount": 6000, "type": "5411", "use_chip": "swipe", "errors": "Invalid PIN"}
    r = client.post("/api/fraud/predict", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "prediction" in data
    assert "probability" in data

