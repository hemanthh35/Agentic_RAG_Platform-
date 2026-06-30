import logging
from typing import List, Optional, Dict, Any

from app.retrieval.interfaces.strategy_interface import BaseRetrievalStrategy
from app.retrieval.orchestrator.pipeline import RetrievalPipeline
from app.retrieval.schemas.query import RetrievalResultItem

logger = logging.getLogger(__name__)


class KeywordRetrievalStrategy(BaseRetrievalStrategy):
    """Retrieval strategy prioritizing traditional keyword FTS search indices."""

    def __init__(self, pipeline: RetrievalPipeline):
        self.pipeline = pipeline

    @property
    def name(self) -> str:
        return "keyword"

    async def execute(
        self,
        query: str,
        limit: int,
        threshold: float,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResultItem]:
        logger.info(f"Executing keyword retrieval strategy for query '{query}' (threshold={threshold})")
        results = await self.pipeline.execute_parallel(query, limit, filters)
        return [r for r in results if r.score >= threshold]
