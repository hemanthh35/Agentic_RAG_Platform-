from fastapi import APIRouter
from app.api.v1.endpoints import health

api_router = APIRouter()

# Include health endpoints under the "/health" route prefix
api_router.include_router(health.router, prefix="/health", tags=["Health"])
