from fastapi import APIRouter

router = APIRouter(
    prefix="/api/system",
    tags=["system"],
)


@router.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "uptime": "0s",
        "dataset_loaded": False,
    }
from fastapi import APIRouter, HTTPException

from banking_api.services.system_service import debug_info, health_status, metrics_info
from banking_api.services.transactions_service import DatasetNotLoadedError

router = APIRouter(
    prefix="/api/system",
    tags=["system"],
)


# (déjà existante chez toi, mais on la garde propre)
@router.get("/health")
def health() -> dict:
    return health_status()


# ✅ Route #19
@router.get("/debug")
def debug() -> dict:
    return debug_info()


# ✅ Route #20
@router.get("/metrics")
def metrics() -> dict:
    try:
        return metrics_info()
    except DatasetNotLoadedError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
