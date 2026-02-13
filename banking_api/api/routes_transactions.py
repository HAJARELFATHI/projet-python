from fastapi import APIRouter, Body, HTTPException, Query
from banking_api.services.transactions_service import mark_transaction_deleted

from banking_api.services.transactions_service import (
    DatasetNotLoadedError,
    get_recent_transactions,
    get_transaction_by_id,
    get_transaction_types,
    list_transactions,
    search_transactions,
)
from banking_api.services.transactions_service import (
    get_transactions_by_customer,
    get_transactions_to_customer,
)

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("")
def get_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    type: str | None = None,
    isFraud: int | None = Query(None, ge=0, le=1),
    min_amount: float | None = None,
    max_amount: float | None = None,
) -> dict:
    try:
        return list_transactions(
            page=page,
            limit=limit,
            type=type,
            isFraud=isFraud,
            min_amount=min_amount,
            max_amount=max_amount,
        )
    except DatasetNotLoadedError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/types")
def list_types() -> dict[str, list[str]]:
    try:
        return {"types": get_transaction_types()}
    except DatasetNotLoadedError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/recent")
def recent_transactions(n: int = Query(10, ge=1, le=200)) -> dict:
    try:
        results = get_recent_transactions(n)
    except DatasetNotLoadedError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"count": len(results), "transactions": results}


@router.post("/search")
def search(criteria: dict = Body(...)) -> dict:
    try:
        results = search_transactions(criteria)
    except DatasetNotLoadedError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"count": len(results), "results": results}
@router.get("/by-customer/{customer_id}")
def transactions_by_customer(customer_id: str, limit: int = Query(200, ge=1, le=500)) -> dict:
    results = get_transactions_by_customer(customer_id, limit=limit)
    return {"customer_id": customer_id, "count": len(results), "transactions": results}


@router.get("/to-customer/{customer_id}")
def transactions_to_customer(customer_id: str, limit: int = Query(200, ge=1, le=500)) -> dict:
    results = get_transactions_to_customer(customer_id, limit=limit)
    return {"customer_id": customer_id, "count": len(results), "transactions": results}

@router.delete("/{id}")
def delete_transaction(id: str) -> dict:
    deleted = mark_transaction_deleted(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"deleted": True, "id": id}

@router.get("/{id}")
def get_transaction(id: str) -> dict:
    try:
        tx = get_transaction_by_id(id)
    except DatasetNotLoadedError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx
