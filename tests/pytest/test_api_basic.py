def test_system_health(client):
    r = client.get("/api/system/health")
    assert r.status_code == 200


def test_transactions_list(client):
    r = client.get("/api/transactions?limit=2")
    assert r.status_code == 200, r.text
    data = r.json()
    assert "transactions" in data
    assert data["limit"] == 2


def test_transactions_types(client):
    r = client.get("/api/transactions/types")
    assert r.status_code == 200, r.text
    data = r.json()
    assert "types" in data
    assert len(data["types"]) > 0


def test_stats_overview(client):
    r = client.get("/api/stats/overview")
    assert r.status_code == 200, r.text
    data = r.json()
    assert "total_transactions" in data


def test_fraud_predict(client):
    payload = {"amount": 6000, "type": "5411", "use_chip": "swipe", "errors": "Invalid PIN"}
    r = client.post("/api/fraud/predict", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "prediction" in data
    assert "probability" in data
