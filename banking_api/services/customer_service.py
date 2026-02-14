from __future__ import annotations

from banking_api.services.transactions_service import get_dataset


def list_customers(page: int = 1, limit: int = 50) -> dict:
    df = get_dataset()

    grouped = (
        df.groupby("nameOrig")
        .agg(
            transaction_count=("id", "count"),
            total_amount=("amount", "sum"),
            fraud_count=("isFraud", "sum"),
        )
        .reset_index()
        .rename(columns={"nameOrig": "customer_id"})
    )

    total = int(len(grouped))
    start = (page - 1) * limit
    end = start + limit
    page_df = grouped.iloc[start:end]

    customers = []
    for _, row in page_df.iterrows():
        customers.append(
            {
                "customer_id": str(row["customer_id"]),
                "transaction_count": int(row["transaction_count"]),
                "total_amount": float(row["total_amount"]),
                "fraud_count": int(row["fraud_count"]),
            }
        )

    return {"page": page, "limit": limit, "total": total, "customers": customers}


def get_customer(customer_id: str) -> dict | None:
    df = get_dataset()
    sub = df[df["nameOrig"].astype(str) == str(customer_id)]
    if sub.empty:
        return None

    return {
        "customer_id": str(customer_id),
        "transaction_count": int(len(sub)),
        "total_amount": float(sub["amount"].sum()),
        "fraud_count": int(sub["isFraud"].sum()),
    }


def get_customer_stats(customer_id: str) -> dict | None:
    df = get_dataset()
    sub = df[df["nameOrig"].astype(str) == str(customer_id)]
    if sub.empty:
        return None

    most_common_type = None
    if "type" in sub.columns and not sub["type"].dropna().empty:
        most_common_type = str(sub["type"].mode().iloc[0])

    return {
        "customer_id": str(customer_id),
        "transaction_count": int(len(sub)),
        "total_amount": float(sub["amount"].sum()),
        "avg_amount": float(sub["amount"].mean()),
        "fraud_count": int(sub["isFraud"].sum()),
        "fraud_rate": float(sub["isFraud"].mean()),
        "most_common_type": most_common_type,
    }
