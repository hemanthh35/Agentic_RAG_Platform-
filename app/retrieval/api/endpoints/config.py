from fastapi import APIRouter, Depends, status

from app.retrieval.services.retrieval_service import RetrievalService
from app.retrieval.dependencies.dependencies import get_retrieval_service
from app.retrieval.config.settings import retrieval_settings

router = APIRouter()


@router.get(
    "/config",
    status_code=status.HTTP_200_OK,
    summary="Retrieve active engine search parameters"
)
def get_search_configuration(
    service: RetrievalService = Depends(get_retrieval_service)
):
    """Exposes default limits, thresholds, strategies and connector flags."""
    return {
        "default_limit": retrieval_settings.DEFAULT_RETRIEVAL_LIMIT,
        "default_threshold": retrieval_settings.DEFAULT_SIMILARITY_THRESHOLD,
        "default_strategy": retrieval_settings.DEFAULT_RETRIEVAL_STRATEGY,
        "registered_strategies": service.orchestrator.registered_strategies,
        "features": {
            "semantic_search": retrieval_settings.ENABLE_SEMANTIC_SEARCH,
            "keyword_search": retrieval_settings.ENABLE_KEYWORD_SEARCH,
            "hybrid_search": retrieval_settings.ENABLE_HYBRID_SEARCH
        }
    }
