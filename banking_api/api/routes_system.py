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
