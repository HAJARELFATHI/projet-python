from fastapi import APIRouter
from banking_api.services.fraud_detection_service import get_fraud_by_type
from fastapi import Body
from banking_api.services.fraud_detection_service import predict_fraud


router = APIRouter(
    prefix="/api/fraud",
    tags=["fraud"],
)
from fastapi import APIRouter, HTTPException

from banking_api.services.fraud_detection_service import get_fraud_summary
from banking_api.services.transactions_service import DatasetNotLoadedError

router = APIRouter(
    prefix="/api/fraud",
    tags=["fraud"],
)


@router.get("/summary")
def fraud_summary() -> dict:
    """
    Route #13: Fraud global summary.
    """
    try:
        return get_fraud_summary()
    except DatasetNotLoadedError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/by-type")
def fraud_by_type() -> list[dict]:
    """
    Route #14: Fraud grouped by type.
    """
    return get_fraud_by_type()


@router.post("/predict")
def fraud_predict(payload: dict = Body(...)) -> dict:
    """
    Route #15: Predict fraud risk for a transaction (heuristic model).
    """
    return predict_fraud(payload)
