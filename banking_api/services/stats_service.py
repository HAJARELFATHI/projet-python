from __future__ import annotations

from typing import Any

from banking_api.services.transactions_service import get_dataset
import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from banking_api.services.customer_service import (
    get_customer,
    get_customer_stats,
    list_customers,
)
from banking_api.services.transactions_service import DatasetNotLoadedError

def get_overview_stats() -> dict[str, Any]:
    """
    Global statistics overview of the dataset.

    Returns
    -------
    dict
        total_transactions, fraud_rate, avg_amount, most_common_type
    """
    df = get_dataset()

    total_transactions = int(len(df))

    # Avoid division by zero
    if total_transactions == 0:
        return {
            "total_transactions": 0,
            "fraud_rate": 0.0,
            "avg_amount": 0.0,
            "most_common_type": None,
        }

    avg_amount = float(df["amount"].mean())

    # Fraud rate (isFraud is 0/1)
    fraud_rate = float(df["isFraud"].mean())

    # Most common type (mode)
    most_common_type = None
    if "type" in df.columns and not df["type"].dropna().empty:
        most_common_type = str(df["type"].mode().iloc[0])

    return {
        "total_transactions": total_transactions,
        "fraud_rate": fraud_rate,
        "avg_amount": avg_amount,
        "most_common_type": most_common_type,
    }
def get_amount_distribution() -> dict[str, list]:
    """
    Return histogram distribution of transaction amounts.
    """
    df = get_dataset()

    if df.empty:
        return {"bins": [], "counts": []}

    # Define bins manually (spec-like)
    bins = [0, 100, 500, 1000, 5000, float("inf")]
    labels = ["0-100", "100-500", "500-1000", "1000-5000", "5000+"]

    df["amount_bin"] = pd.cut(
        df["amount"],
        bins=bins,
        labels=labels,
        include_lowest=True,
        right=False,
    )

    counts = df["amount_bin"].value_counts().sort_index()

    return {
        "bins": labels,
        "counts": [int(counts.get(label, 0)) for label in labels],
    }

def get_stats_by_type() -> list[dict]:
    """
    Return statistics grouped by transaction type.
    """
    df = get_dataset()

    if df.empty:
        return []

    grouped = df.groupby("type").agg(
        count=("id", "count"),
        avg_amount=("amount", "mean"),
    ).reset_index()

    results = []
    for _, row in grouped.iterrows():
        results.append({
            "type": str(row["type"]),
            "count": int(row["count"]),
            "avg_amount": float(row["avg_amount"]),
        })

    return results

def get_daily_stats() -> list[dict]:
    """
    Return daily transaction statistics.
    """
    df = get_dataset()

    if df.empty or "date" not in df.columns:
        return []

    # Convert date column
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    grouped = df.groupby(df["date"].dt.date).agg(
        count=("id", "count"),
        avg_amount=("amount", "mean"),
    ).reset_index()

    results = []
    for _, row in grouped.iterrows():
        results.append({
            "date": str(row["date"]),
            "count": int(row["count"]),
            "avg_amount": float(row["avg_amount"]),
        })

    return results
