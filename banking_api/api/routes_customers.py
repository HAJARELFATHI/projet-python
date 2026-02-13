from fastapi import APIRouter

router = APIRouter(
    prefix="/api/customers",
    tags=["customers"],
)
