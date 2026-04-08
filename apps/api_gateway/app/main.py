from fastapi import FastAPI
from apps.api_gateway.app.api.routes.health import router as health_router
from apps.api_gateway.app.api.routes.jobs import router as jobs_router
from apps.api_gateway.app.api.routes.approvals import router as approvals_router
from apps.api_gateway.app.api.routes.products import router as products_router
from apps.api_gateway.app.services.bootstrap import init_db

app = FastAPI(title="Local Commerce AI API", version="0.2.0")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
app.include_router(approvals_router, prefix="/approvals", tags=["approvals"])
app.include_router(products_router, prefix="/products", tags=["products"])
