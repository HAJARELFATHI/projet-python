
from fastapi import APIRouter, HTTPException, Query

from banking_api.services.customer_service import (
    get_customer,
    get_customer_stats,
    list_customers,
)
from banking_api.services.transactions_service import DatasetNotLoadedError

router = APIRouter(
    prefix="/api/customers",
    tags=["customers"],
)


# Route #16
@router.get("")
def customers(page: int = Query(1, ge=1), limit: int = Query(50, ge=1, le=200)) -> dict:
    try:
        return list_customers(page=page, limit=limit)
    except DatasetNotLoadedError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# Route #17
@router.get("/{customer_id}")
def customer(customer_id: str) -> dict:
    try:
        res = get_customer(customer_id)
    except DatasetNotLoadedError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if res is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return res


# Route #18
@router.get("/{customer_id}/stats")
def customer_stats(customer_id: str) -> dict:
    try:
        res = get_customer_stats(customer_id)
    except DatasetNotLoadedError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if res is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return res
