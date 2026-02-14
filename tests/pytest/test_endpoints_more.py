def test_system_debug(client):
    r = client.get("/api/system/debug")
    assert r.status_code == 200, r.text
    data = r.json()
    assert "python_version" in data
    assert "dataset_loaded" in data


def test_system_metrics(client):
    r = client.get("/api/system/metrics")
    assert r.status_code == 200, r.text
    data = r.json()
    assert "total_transactions" in data


def test_stats_amount_distribution(client):
    r = client.get("/api/stats/amount-distribution")
    assert r.status_code == 200, r.text
    data = r.json()
    assert "bins" in data and "counts" in data
    assert len(data["bins"]) == len(data["counts"])


def test_stats_by_type(client):
    r = client.get("/api/stats/by-type")
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data, list)


def test_stats_daily(client):
    r = client.get("/api/stats/daily")
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data, list)


def test_fraud_summary(client):
    r = client.get("/api/fraud/summary")
    assert r.status_code == 200, r.text
    data = r.json()
    assert "total_frauds" in data


def test_fraud_by_type(client):
    r = client.get("/api/fraud/by-type")
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data, list)


def test_transactions_recent(client):
    r = client.get("/api/transactions/recent?n=2")
    assert r.status_code == 200, r.text
    data = r.json()
    assert "transactions" in data
    assert data["count"] == 2


def test_transactions_search_type(client):
    # This must exist in tests/data/mcc_codes.json mapping (5411 => Grocery Stores, Supermarkets)
    body = {"type": "Grocery Stores, Supermarkets"}
    r = client.post("/api/transactions/search", json=body)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "results" in data


def test_transactions_get_by_id(client):
    # Get a real id from list endpoint, then fetch details
    r = client.get("/api/transactions?limit=1")
    assert r.status_code == 200, r.text
    tx_id = r.json()["transactions"][0]["id"]

    r2 = client.get(f"/api/transactions/{tx_id}")
    assert r2.status_code == 200, r2.text
    data = r2.json()
    assert data["id"] == tx_id


def test_transactions_by_customer(client):
    r = client.get("/api/transactions/by-customer/1556?limit=5")
    assert r.status_code == 200, r.text
    data = r.json()
    assert "transactions" in data


def test_transactions_to_customer(client):
    r = client.get("/api/transactions/to-customer/59935?limit=5")
    assert r.status_code == 200, r.text
    data = r.json()
    assert "transactions" in data


def test_transactions_delete_then_404(client):
    # pick an existing transaction id
    r = client.get("/api/transactions?limit=1")
    assert r.status_code == 200, r.text
    tx_id = r.json()["transactions"][0]["id"]

    d = client.delete(f"/api/transactions/{tx_id}")
    assert d.status_code in (200, 204), d.text

    g = client.get(f"/api/transactions/{tx_id}")
    assert g.status_code == 404, g.text


def test_customers_list(client):
    r = client.get("/api/customers?page=1&limit=2")
    assert r.status_code == 200, r.text
    data = r.json()
    assert "customers" in data
    assert data["limit"] == 2


def test_customers_detail_and_stats(client):
    # take a customer id from list
    r = client.get("/api/customers?page=1&limit=1")
    assert r.status_code == 200, r.text
    customer_id = r.json()["customers"][0]["customer_id"]

    r2 = client.get(f"/api/customers/{customer_id}")
    assert r2.status_code == 200, r2.text

    r3 = client.get(f"/api/customers/{customer_id}/stats")
    assert r3.status_code == 200, r3.text
    data = r3.json()
    assert data["customer_id"] == customer_id
