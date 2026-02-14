from fastapi import APIRouter, HTTPException

from banking_api.services.stats_service import get_overview_stats
from banking_api.services.transactions_service import DatasetNotLoadedError
from banking_api.services.stats_service import get_amount_distribution
from banking_api.services.stats_service import get_stats_by_type
router = APIRouter(
    prefix="/api/stats",
    tags=["stats"],
)


@router.get("/overview")
def stats_overview() -> dict:
    """
    Route #9: Global dataset statistics overview.
    """
    try:
        return get_overview_stats()
    except DatasetNotLoadedError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.get("/amount-distribution")
def amount_distribution() -> dict:
    """
    Route #10: Histogram of transaction amounts.
    """
    return get_amount_distribution()

@router.get("/by-type")
def stats_by_type() -> list[dict]:
    """
    Route #11: Stats grouped by type.
    """
    return get_stats_by_type()

from banking_api.services.stats_service import get_daily_stats


@router.get("/daily")
def stats_daily() -> list[dict]:
    """
    Route #12: Daily statistics.
    """
    return get_daily_stats()
