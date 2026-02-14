from typing import Any

from banking_api.services.transactions_service import get_dataset
import math

def get_fraud_summary() -> dict[str, Any]:
    """
    Return global fraud summary.
    """
    df = get_dataset()

    total_frauds = int(df["isFraud"].sum())

    total_transactions = len(df)

    fraud_rate = 0.0
    if total_transactions > 0:
        fraud_rate = float(total_frauds / total_transactions)

    # Since we do not have a real prediction model yet:
    flagged = 0
    precision = 1.0
    recall = 1.0

    return {
        "total_frauds": total_frauds,
        "flagged": flagged,
        "precision": precision,
        "recall": recall,
        "fraud_rate": fraud_rate,
    }

def get_fraud_by_type() -> list[dict]:
    """
    Return fraud count grouped by transaction type.
    """
    df = get_dataset()

    if df.empty:
        return []

    # Only keep fraud transactions
    fraud_df = df[df["isFraud"] == 1]

    if fraud_df.empty:
        return []

    grouped = fraud_df.groupby("type").size().reset_index(name="fraud_count")

    results = []
    for _, row in grouped.iterrows():
        results.append({
            "type": str(row["type"]),
            "fraud_count": int(row["fraud_count"]),
        })

    return results
def get_fraud_by_type() -> list[dict]:
    """
    Return fraud count grouped by transaction type.
    """
    df = get_dataset()

    fraud_df = df[df["isFraud"] == 1]
    if fraud_df.empty:
        return []

    grouped = fraud_df.groupby("type").size().reset_index(name="fraud_count")

    return [
        {"type": str(row["type"]), "fraud_count": int(row["fraud_count"])}
        for _, row in grouped.iterrows()
    ]

def predict_fraud(payload: dict) -> dict:
    """
    Simple heuristic fraud predictor.

    Expected payload keys (dataset-adapted):
    - amount (float)
    - type (str) : we accept MCC name or MCC code
    - use_chip (str) optional
    - errors (str) optional
    """
    amount = float(payload.get("amount", 0.0) or 0.0)
    use_chip = str(payload.get("use_chip", "") or "").lower()
    errors = str(payload.get("errors", "") or "").strip()
    tx_type = str(payload.get("type", "") or "").strip()

    # Heuristic risk score (0..100)
    score = 0.0

    # Amount contribution
    if amount >= 5000:
        score += 50
    elif amount >= 1000:
        score += 35
    elif amount >= 500:
        score += 20
    elif amount >= 100:
        score += 10

    # Errors contribution
    if errors != "":
        score += 35

    # Chip usage (slightly safer)
    if "chip" in use_chip:
        score -= 10

    # Unknown/empty type adds slight risk
    if tx_type == "":
        score += 5

    # Clamp score
    score = max(0.0, min(100.0, score))

    # Convert score -> probability (smooth)
    # Center at 50, scale 12
    probability = 1.0 / (1.0 + math.exp(-(score - 50.0) / 12.0))

    prediction = 1 if probability >= 0.5 else 0

    return {
        "prediction": prediction,
        "probability": float(round(probability, 4)),
        "risk_score": float(round(score, 2)),
    }

