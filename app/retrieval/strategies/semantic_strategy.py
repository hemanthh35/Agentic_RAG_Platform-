import logging
from typing import List, Optional, Dict, Any

from app.retrieval.interfaces.strategy_interface import BaseRetrievalStrategy
from app.retrieval.interfaces.provider_interface import BaseRetrievalProvider
from app.retrieval.schemas.query import RetrievalResultItem

logger = logging.getLogger(__name__)


class SemanticRetrievalStrategy(BaseRetrievalStrategy):
    """Retrieval strategy prioritizing semantic/vector search indices."""

    def __init__(self, providers: List[BaseRetrievalProvider]):
        self.providers = providers

    @property
    def name(self) -> str:
        return "semantic"

    async def execute(
        self,
        query: str,
        limit: int,
        threshold: float,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResultItem]:
        logger.info(f"Executing semantic retrieval strategy for query '{query}' (threshold={threshold})")
        for provider in self.providers:
            if provider.name in ("qdrant", "mock"):
                results = await provider.retrieve(query, limit, filters)
                filtered = [r for r in results if r.score >= threshold]
                if filtered:
                    return filtered
        return []
