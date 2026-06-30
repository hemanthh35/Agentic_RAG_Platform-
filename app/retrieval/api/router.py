from fastapi import APIRouter
from app.retrieval.api.endpoints import search, config

router = APIRouter()

router.include_router(search.router)
router.include_router(config.router)
