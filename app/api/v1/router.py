from fastapi import APIRouter
from app.api.v1.endpoints import health, documents

api_router = APIRouter()

# Include health endpoints under the "/health" route prefix
api_router.include_router(health.router, prefix="/health", tags=["Health"])

# Include documents endpoints under the "/documents" route prefix
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
