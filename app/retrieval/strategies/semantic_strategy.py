import logging
from typing import List, Optional, Dict, Any

from app.retrieval.interfaces.strategy_interface import BaseRetrievalStrategy
from app.retrieval.orchestrator.pipeline import RetrievalPipeline
from app.retrieval.schemas.query import RetrievalResultItem
from app.retrieval.context.retrieval_context import RetrievalContext

logger = logging.getLogger(__name__)


class SemanticRetrievalStrategy(BaseRetrievalStrategy):
    """Retrieval strategy prioritizing semantic/vector search indices."""

    def __init__(self, pipeline: RetrievalPipeline):
        self.pipeline = pipeline

    @property
    def name(self) -> str:
        return "semantic"

    async def execute(
        self,
        context: RetrievalContext
    ) -> List[RetrievalResultItem]:
        correlation_id = context.tracing.correlation_id
        threshold = context.configuration.similarity_threshold
        query = context.query.original_query
        
        logger.info(
            f"[CorrelationID: {correlation_id}] Executing semantic retrieval strategy for query '{query}' (threshold={threshold})"
        )
        results = await self.pipeline.execute_parallel(context)
        return [r for r in results if r.score >= threshold]

