from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import json
import pandas as pd
DELETED_TX_IDS: set[str] = set()

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.environ.get("DATA_DIR", BASE_DIR / "data"))

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

TX_PATH = DATA_DIR / "transactions_data.csv"
USERS_PATH = DATA_DIR / "users_data.csv"
CARDS_PATH = DATA_DIR / "cards_data.csv"
MCC_PATH = DATA_DIR / "mcc_codes.json"
FRAUD_LABELS_PATH = DATA_DIR / "train_fraud_labels.json"


class DatasetNotLoadedError(RuntimeError):
    """Raised when the dataset cannot be loaded."""


def _require_file(path: Path) -> None:
    if not path.exists():
        raise DatasetNotLoadedError(f"Missing file: {path}")


@lru_cache(maxsize=1)
def load_mcc_mapping() -> dict[str, str]:
    """Load MCC codes mapping as {mcc_code: mcc_name}."""
    _require_file(MCC_PATH)
    with MCC_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # Kaggle MCC JSON is usually { "5411": "Grocery Stores, Supermarkets", ... }
    mapping: dict[str, str] = {}
    for k, v in data.items():
        mapping[str(k)] = str(v)
    return mapping


@lru_cache(maxsize=1)
def load_fraud_labels() -> dict[str, int]:
    """
    Load fraud labels mapping as {transaction_id: 0/1}.
    If the JSON structure differs, we handle common shapes.
    """
    _require_file(FRAUD_LABELS_PATH)
    with FRAUD_LABELS_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    labels: dict[str, int] = {}

    # Common shapes:
    # 1) {"txid1": 0, "txid2": 1, ...}
    if isinstance(data, dict):
        for k, v in data.items():
            try:
                labels[str(k)] = int(v)
            except Exception:
                continue
        return labels

    # 2) [{"id": "...", "isFraud": 1}, ...]
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                txid = item.get("id") or item.get("transaction_id") or item.get("txid")
                val = item.get("isFraud") or item.get("label") or item.get("fraud")
                if txid is not None and val is not None:
                    try:
                        labels[str(txid)] = int(val)
                    except Exception:
                        continue
        return labels

    return labels


@lru_cache(maxsize=1)
def get_dataset() -> pd.DataFrame:
    """
    Load and normalize the dataset to match the teacher's API spec columns.

    Output columns include at least:
    - id, amount, type, isFraud, nameOrig, nameDest
    """
    _require_file(TX_PATH)

    try:
        tx = pd.read_csv(TX_PATH)
    except Exception as exc:  # noqa: BLE001
        raise DatasetNotLoadedError(f"Failed to load transactions_data.csv: {exc}") from exc

    # Normalize base columns
    # Expected input columns: id, client_id, merchant_id, amount, mcc, errors, ...
    for col in ["id", "client_id", "merchant_id", "amount", "mcc"]:
        if col not in tx.columns:
            raise DatasetNotLoadedError(f"transactions_data.csv missing required column: {col}")

    tx["id"] = tx["id"].astype(str)
    tx["nameOrig"] = tx["client_id"].astype(str)
    tx["nameDest"] = tx["merchant_id"].astype(str)

    # type = MCC name if possible, else MCC code
    mcc_map = load_mcc_mapping()
    tx["type"] = tx["mcc"].astype(str).map(mcc_map).fillna(tx["mcc"].astype(str))

    # isFraud from labels file (if not present => 0)
    labels = load_fraud_labels()
    tx["isFraud"] = tx["id"].map(labels).fillna(0).astype(int)

    # Keep original useful columns too (optional)
    # Ensure amount numeric
    tx["amount"] = pd.to_numeric(tx["amount"], errors="coerce").fillna(0.0)

    return tx


def get_transaction_types() -> list[str]:
    """Unique list of 'type' values (MCC names)."""
    df = get_dataset()
    types = df["type"].dropna().astype(str).unique().tolist()
    return sorted(types)


def list_transactions(
    page: int = 1,
    limit: int = 50,
    type: str | None = None,  # keep spec param name
    isFraud: int | None = None,
    min_amount: float | None = None,
    max_amount: float | None = None,
) -> dict[str, Any]:
    """Spec-like paginated list with filters."""
    if page < 1:
        page = 1
    if limit < 1:
        limit = 1
    if limit > 200:
        limit = 200

    df = get_dataset()
    filtered = df
    if DELETED_TX_IDS:
        filtered = filtered[~filtered["id"].isin(DELETED_TX_IDS)]

    if type is not None:
        filtered = filtered[filtered["type"].astype(str) == str(type)]

    if isFraud is not None:
        filtered = filtered[filtered["isFraud"].astype(int) == int(isFraud)]

    if min_amount is not None:
        filtered = filtered[filtered["amount"] >= float(min_amount)]

    if max_amount is not None:
        filtered = filtered[filtered["amount"] <= float(max_amount)]

    total = int(len(filtered))
    start = (page - 1) * limit
    end = start + limit
    page_df = filtered.iloc[start:end].copy()

    # Return minimal fields like spec example
    items = page_df[["id", "amount", "type", "isFraud", "nameOrig", "nameDest"]].to_dict(orient="records")

    return {"page": page, "limit": limit, "total": total, "transactions": items}


def get_transaction_by_id(tx_id: str) -> dict[str, Any] | None:
    """Return one transaction record by id (spec route #2)."""
    if is_transaction_deleted(tx_id):
        return None

    df = get_dataset()
    match = df[df["id"] == str(tx_id)]
    if match.empty:
        return None
    row = match.iloc[0]
    return {
        "id": str(row["id"]),
        "amount": float(row["amount"]),
        "type": str(row["type"]),
        "isFraud": int(row["isFraud"]),
        "nameOrig": str(row["nameOrig"]),
        "nameDest": str(row["nameDest"]),
    }
def search_transactions(criteria: dict) -> list[dict]:
    """
    Multi-criteria search (POST body).
    Supported keys:
    - type
    - isFraud
    - amount_range: [min, max]
    """
    df = get_dataset()
    filtered = df

    tx_type = criteria.get("type")
    is_fraud = criteria.get("isFraud")
    amount_range = criteria.get("amount_range")

    if tx_type is not None:
        filtered = filtered[filtered["type"].astype(str) == str(tx_type)]

    if is_fraud is not None:
        filtered = filtered[filtered["isFraud"].astype(int) == int(is_fraud)]

    if amount_range and isinstance(amount_range, list) and len(amount_range) == 2:
        min_val, max_val = amount_range
        filtered = filtered[
            (filtered["amount"] >= float(min_val)) &
            (filtered["amount"] <= float(max_val))
        ]

    return filtered[["id", "amount", "type", "isFraud", "nameOrig", "nameDest"]] \
        .head(100) \
        .to_dict(orient="records")

def get_recent_transactions(n: int = 10) -> list[dict]:
    """
    Return N most recent transactions based on 'date' column.
    """
    df = get_dataset()

    if "date" not in df.columns:
        # If no date column, just return first N rows
        recent = df.head(n)
    else:
        recent = df.sort_values("date", ascending=False).head(n)

    return recent[["id", "amount", "type", "isFraud", "nameOrig", "nameDest"]] \
        .to_dict(orient="records")

def mark_transaction_deleted(tx_id: str) -> bool:
    """
    Mark a transaction as deleted (fake delete for test mode).

    Returns True if transaction exists and is now marked as deleted, else False.
    """
    existing = get_transaction_by_id(tx_id)
    if existing is None:
        return False
    DELETED_TX_IDS.add(str(tx_id))
    return True


def is_transaction_deleted(tx_id: str) -> bool:
    """Check if a transaction is marked as deleted."""
    return str(tx_id) in DELETED_TX_IDS

def get_transactions_by_customer(customer_id: str, limit: int = 200) -> list[dict]:
    """Transactions where customer is origin (nameOrig)."""
    df = get_dataset()
    filtered = df[df["nameOrig"].astype(str) == str(customer_id)]
    if DELETED_TX_IDS:
        filtered = filtered[~filtered["id"].isin(DELETED_TX_IDS)]
    return filtered[["id", "amount", "type", "isFraud", "nameOrig", "nameDest"]].head(limit).to_dict(orient="records")


def get_transactions_to_customer(customer_id: str, limit: int = 200) -> list[dict]:
    """Transactions where customer is destination (nameDest)."""
    df = get_dataset()
    filtered = df[df["nameDest"].astype(str) == str(customer_id)]
    if DELETED_TX_IDS:
        filtered = filtered[~filtered["id"].isin(DELETED_TX_IDS)]
    return filtered[["id", "amount", "type", "isFraud", "nameOrig", "nameDest"]].head(limit).to_dict(orient="records")
