import time
import logging

from app.retrieval.interfaces.service_interface import BaseRetrievalService
from app.retrieval.orchestrator.retrieval_orchestrator import RetrievalOrchestrator
from app.retrieval.services.validation_service import ValidationService
from app.retrieval.services.context_service import ContextService
from app.retrieval.cache.cache_manager import BaseCacheManager
from app.retrieval.repositories.retrieval_repository import RetrievalRepository
from app.retrieval.schemas.query import RetrievalRequest, RetrievalResponse
from app.retrieval.config.settings import retrieval_settings

logger = logging.getLogger(__name__)


class RetrievalService(BaseRetrievalService):
    """High-level coordinate service managing search parameters, validation, and analytics logging."""

    def __init__(
        self,
        orchestrator: RetrievalOrchestrator,
        validation_service: ValidationService,
        context_service: ContextService,
        cache_manager: BaseCacheManager,
        retrieval_repository: RetrievalRepository
    ):
        self.orchestrator = orchestrator
        self.validation_service = validation_service
        self.context_service = context_service
        self.cache_manager = cache_manager
        self.retrieval_repository = retrieval_repository

    async def retrieve_context(self, request: RetrievalRequest) -> RetrievalResponse:
        """Coordinated retrieval run cycle: validates query -> checks cache -> queries orchestrator."""
        start_time = time.time()
        
        # 1. Validation & Input Sanitization
        query_text = self.validation_service.validate_request_query(request.query)
        
        # 2. Check Cache
        cache_key = f"query:{query_text}:limit:{request.limit}:strat:{request.strategy}"
        cached_results = self.cache_manager.get(cache_key)
        if cached_results is not None:
            logger.info(f"Retrieval Cache HIT for key: {cache_key}")
            execution_time_ms = (time.time() - start_time) * 1000
            return RetrievalResponse(
                query=query_text,
                items=cached_results,
                total_results=len(cached_results),
                execution_time_ms=round(execution_time_ms, 2),
                strategy_used=request.strategy,
                providers_queried=["cache"]
            )

        logger.info(f"Retrieval Cache MISS for key: {cache_key}")

        # 3. Execution through Orchestrated Strategy
        limit = request.limit if request.limit else retrieval_settings.DEFAULT_RETRIEVAL_LIMIT
        threshold = request.threshold if request.threshold is not None else retrieval_settings.DEFAULT_SIMILARITY_THRESHOLD
        
        items = await self.orchestrator.execute_retrieval(
            query=query_text,
            limit=limit,
            threshold=threshold,
            strategy_name=request.strategy,
            filters=request.filters
        )

        execution_time_ms = (time.time() - start_time) * 1000

        # 4. Save to Cache
        self.cache_manager.set(
            key=cache_key,
            value=items,
            ttl_seconds=retrieval_settings.CACHE_EXPIRATION_SECONDS
        )

        # 5. Log Analytics
        self.retrieval_repository.log_search(
            query=query_text,
            strategy=request.strategy,
            result_count=len(items),
            latency_ms=execution_time_ms
        )

        # Identify active source providers based on strategy structure
        providers_queried = []
        strategy_lower = request.strategy.lower()
        if strategy_lower == "semantic":
            providers_queried = ["qdrant"]
        elif strategy_lower == "keyword":
            providers_queried = ["postgres"]
        else:
            providers_queried = ["qdrant", "postgres"]

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
