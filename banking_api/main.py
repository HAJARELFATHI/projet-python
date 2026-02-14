from fastapi import FastAPI

from banking_api.api.routes_system import router as system_router
from banking_api.api.routes_transactions import router as transactions_router
from banking_api.api.routes_stats import router as stats_router
from banking_api.api.routes_fraud import router as fraud_router
from banking_api.api.routes_customers import router as customers_router
from banking_api.api.routes_stats import router as stats_router

app = FastAPI(
    title="Banking Transactions API",
    version="1.0.0",
    description="API for banking transactions exposure",
)

# Include routers
app.include_router(system_router)
app.include_router(transactions_router)
app.include_router(stats_router)
app.include_router(fraud_router)
app.include_router(customers_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Banking Transactions API is running"}
