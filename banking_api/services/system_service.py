from __future__ import annotations

import platform
import sys
import time
from typing import Any

from banking_api.services.transactions_service import DatasetNotLoadedError, get_dataset

START_TIME = time.time()


def get_uptime_seconds() -> int:
    return int(time.time() - START_TIME)


def health_status() -> dict[str, Any]:
    """
    Route #19 (part): Basic health information.
    """
    dataset_loaded = True
    try:
        _ = get_dataset()
    except DatasetNotLoadedError:
        dataset_loaded = False

    return {
        "status": "ok",
        "uptime": f"{get_uptime_seconds()}s",
        "dataset_loaded": dataset_loaded,
    }


def debug_info() -> dict[str, Any]:
    """
    Route #19: Debug endpoint (useful for verifying dataset + environment).
    """
    info: dict[str, Any] = {
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "uptime_seconds": get_uptime_seconds(),
        "dataset_loaded": False,
    }

    try:
        df = get_dataset()
        info["dataset_loaded"] = True
        info["dataset_shape"] = {"rows": int(df.shape[0]), "cols": int(df.shape[1])}
        info["columns"] = [str(c) for c in df.columns.tolist()]
        # small sample (safe)
        info["sample_ids"] = [str(x) for x in df["id"].head(5).tolist()] if "id" in df.columns else []
    except DatasetNotLoadedError as exc:
        info["dataset_error"] = str(exc)

    return info


def metrics_info() -> dict[str, Any]:
    """
    Route #20: Simple metrics about the dataset.
    """
    df = get_dataset()

    total_transactions = int(len(df))
    unique_customers = int(df["nameOrig"].nunique()) if "nameOrig" in df.columns else 0
    unique_merchants = int(df["nameDest"].nunique()) if "nameDest" in df.columns else 0

    fraud_rate = 0.0
    if total_transactions > 0 and "isFraud" in df.columns:
        fraud_rate = float(df["isFraud"].mean())

    return {
        "uptime_seconds": get_uptime_seconds(),
        "total_transactions": total_transactions,
        "unique_customers": unique_customers,
        "unique_merchants": unique_merchants,
        "fraud_rate": fraud_rate,
    }
