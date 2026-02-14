from banking_api.services import transactions_service as ts
from banking_api.services import stats_service as ss
from banking_api.services import customer_service as cs
from banking_api.services import fraud_detection_service as fs


def test_services_transaction_types_and_get_by_id():
    types = ts.get_transaction_types()
    assert isinstance(types, list)
    assert len(types) > 0

    # take a real id from dataset directly
    df = ts.get_dataset()
    tx_id = str(df["id"].iloc[0])

    one = ts.get_transaction_by_id(tx_id)
    assert one is not None
    assert one["id"] == tx_id


def test_services_list_transactions_filters():
    # cover filter branches
    res = ts.list_transactions(page=1, limit=2, isFraud=1)
    assert "transactions" in res

    res2 = ts.list_transactions(page=1, limit=2, min_amount=0, max_amount=10000)
    assert "transactions" in res2

    # type filter using an existing type
    df = ts.get_dataset()
    t = str(df["type"].iloc[0])
    res3 = ts.list_transactions(page=1, limit=2, type=t)
    assert "transactions" in res3


def test_services_recent_and_by_customer():
    recent = ts.get_recent_transactions(2)
    assert isinstance(recent, list)
    assert len(recent) == 2

    df = ts.get_dataset()
    cust = str(df["nameOrig"].iloc[0])
    dest = str(df["nameDest"].iloc[0])

    by_cust = ts.get_transactions_by_customer(cust, limit=10)
    assert isinstance(by_cust, list)

    to_cust = ts.get_transactions_to_customer(dest, limit=10)
    assert isinstance(to_cust, list)


def test_services_delete_flow():
    df = ts.get_dataset()
    tx_id = str(df["id"].iloc[0])

    ok = ts.mark_transaction_deleted(tx_id)
    assert ok is True
    assert ts.get_transaction_by_id(tx_id) is None  # now treated as deleted


def test_stats_services_all():
    ov = ss.get_overview_stats()
    assert "total_transactions" in ov

    dist = ss.get_amount_distribution()
    assert "bins" in dist and "counts" in dist

    bt = ss.get_stats_by_type()
    assert isinstance(bt, list)

    daily = ss.get_daily_stats()
    assert isinstance(daily, list)


def test_customer_services_all():
    lst = cs.list_customers(page=1, limit=2)
    assert "customers" in lst

    # pick an existing customer
    df = ts.get_dataset()
    cid = str(df["nameOrig"].iloc[0])

    c = cs.get_customer(cid)
    assert c is not None

    s = cs.get_customer_stats(cid)
    assert s is not None
    assert "most_common_type" in s


def test_fraud_services_all():
    summ = fs.get_fraud_summary()
    assert "fraud_rate" in summ

    by_type = fs.get_fraud_by_type()
    assert isinstance(by_type, list)

    # cover predict branches directly
    out1 = fs.predict_fraud({"amount": 0, "type": "5411", "use_chip": "chip", "errors": ""})
    out2 = fs.predict_fraud({"amount": 150, "type": "", "use_chip": "", "errors": ""})
    out3 = fs.predict_fraud({"amount": 1200, "type": "", "use_chip": "swipe", "errors": "X"})
    out4 = fs.predict_fraud({"amount": 6000, "type": "5411", "use_chip": "swipe", "errors": "X"})
    assert "prediction" in out1 and "probability" in out1
    assert "prediction" in out2 and "probability" in out2
    assert "prediction" in out3 and "probability" in out3
    assert "prediction" in out4 and "probability" in out4
