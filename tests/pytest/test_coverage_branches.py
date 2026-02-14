def test_transactions_filters(client):
    r = client.get("/api/transactions?limit=2&isFraud=1")
    assert r.status_code == 200, r.text

    r2 = client.get("/api/transactions?limit=2&min_amount=100&max_amount=7000")
    assert r2.status_code == 200, r2.text


def test_transactions_not_found(client):
    r = client.get("/api/transactions/does-not-exist")
    assert r.status_code == 404


def test_customers_not_found(client):
    r = client.get("/api/customers/does-not-exist")
    assert r.status_code == 404
    r2 = client.get("/api/customers/does-not-exist/stats")
    assert r2.status_code == 404


def test_fraud_predict_more_branches(client):
    risky = {"amount": 6000, "type": "", "use_chip": "swipe", "errors": "Invalid PIN"}
    r = client.post("/api/fraud/predict", json=risky)
    assert r.status_code == 200, r.text

    safe = {"amount": 5, "type": "5411", "use_chip": "chip", "errors": ""}
    r2 = client.post("/api/fraud/predict", json=safe)
    assert r2.status_code == 200, r2.text


def test_transactions_search_amount_range(client):
    body = {"amount_range": [0, 200]}
    r = client.post("/api/transactions/search", json=body)
    assert r.status_code == 200, r.text
    assert "results" in r.json()


def test_system_endpoints(client):
    assert client.get("/api/system/health").status_code == 200
    assert client.get("/api/system/debug").status_code == 200
    assert client.get("/api/system/metrics").status_code == 200


def test_stats_endpoints(client):
    assert client.get("/api/stats/overview").status_code == 200
    assert client.get("/api/stats/amount-distribution").status_code == 200
    assert client.get("/api/stats/by-type").status_code == 200
    assert client.get("/api/stats/daily").status_code == 200


def test_customers_list(client):
    r = client.get("/api/customers?page=1&limit=2")
    assert r.status_code == 200, r.text
    data = r.json()
    assert "customers" in data
def test_customers_pagination_params(client):
    # cover Query validation branches (routes_customers missing lines)
    r = client.get("/api/customers?page=1&limit=200")
    assert r.status_code == 200, r.text


def test_transactions_types_and_filters_extra(client):
    # hit a couple of extra lines in routes_transactions
    r = client.get("/api/transactions/types")
    assert r.status_code == 200, r.text

    r2 = client.get("/api/transactions?limit=2&type=Grocery%20Stores,%20Supermarkets")
    assert r2.status_code == 200, r2.text

def test_fraud_predict_mid_amount_branch(client):
    payload = {
        "amount": 300,          # triggers the 100-500 branch
        "type": "5411",
        "use_chip": "",         # no chip branch
        "errors": ""            # no errors branch
    }
    r = client.post("/api/fraud/predict", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "risk_score" in data

def test_fraud_predict_all_branches(client):
    payload = {
        "amount": 700,          # triggers 500+ branch
        "type": "",             # triggers "empty type" branch
        "use_chip": "chip",     # triggers chip discount branch
        "errors": "X"           # triggers errors branch
    }
    r = client.post("/api/fraud/predict", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "prediction" in data and "probability" in data and "risk_score" in data
