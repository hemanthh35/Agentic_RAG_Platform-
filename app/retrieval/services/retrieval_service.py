import time
import logging
from typing import List

from app.retrieval.orchestrator.orchestrator import RetrievalOrchestrator
from app.retrieval.schemas.query import RetrievalRequest, RetrievalResponse
from app.retrieval.config.settings import retrieval_settings

logger = logging.getLogger(__name__)


class RetrievalService:
    """Core service managing the search retrieval pipeline context, validation and latency."""

    def __init__(self, orchestrator: RetrievalOrchestrator):
        self.orchestrator = orchestrator

    async def retrieve_context(self, request: RetrievalRequest) -> RetrievalResponse:
        """Coordinated retrieval cycle: validates query -> sanitizes inputs -> triggers orchestrator."""
        start_time = time.time()
        
        # 1. Validation & Input Sanitization
        query_text = request.query.strip() if request.query else ""
        if not query_text:
            raise ValueError("Query string cannot be empty or whitespace.")

        limit = request.limit if request.limit else retrieval_settings.DEFAULT_RETRIEVAL_LIMIT
        threshold = request.threshold if request.threshold is not None else retrieval_settings.DEFAULT_SIMILARITY_THRESHOLD
        
        logger.info(f"Retrieving context for query: '{query_text}' (limit={limit}, strategy='{request.strategy}')")

        # 2. Execution through Orchestrated Strategy
        try:
            items = await self.orchestrator.execute_retrieval(
                query=query_text,
                limit=limit,
                threshold=threshold,
                strategy_name=request.strategy,
                filters=request.filters
            )
        except Exception as e:
            logger.error(f"Retrieval orchestrator encountered error: {e}")
            raise

        execution_time_ms = (time.time() - start_time) * 1000

        # Identify active source providers based on strategy structure
        providers_queried = []
        strategy_lower = request.strategy.lower()
        if strategy_lower == "semantic":
            providers_queried = ["qdrant"]
        elif strategy_lower == "keyword":
            providers_queried = ["postgres"]
        else:
            providers_queried = ["qdrant", "postgres"]

        # If fallback mock records are returned
        if any("mock" in item.text_content.lower() for item in items):
            providers_queried = ["mock"]

        return RetrievalResponse(
            query=query_text,
            items=items,
            total_results=len(items),
            execution_time_ms=round(execution_time_ms, 2),
            strategy_used=request.strategy,
            providers_queried=providers_queried
        )
