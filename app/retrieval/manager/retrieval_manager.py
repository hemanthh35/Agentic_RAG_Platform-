import time
import logging
from typing import Optional, List, Dict, Any, Union

from app.retrieval.schemas.query import RetrievalRequest, RetrievalResponse, RetrievalResultItem
from app.retrieval.manager.metrics import RetrievalTimelineMetrics
from app.retrieval.manager.validator import RetrievalValidator
from app.retrieval.manager.session_builder import RetrievalSessionBuilder
from app.retrieval.manager.coordinator import RetrievalCoordinator
from app.retrieval.manager.execution_manager import RetrievalExecutionManager
from app.retrieval.manager.result_builder import RetrievalResultBuilder
from app.retrieval.manager.observability import TelemetryManager
from app.retrieval.services.query_processor import QueryProcessor
from app.retrieval.cache.cache_manager import BaseCacheManager
from app.retrieval.repositories.retrieval_repository import RetrievalRepository
from app.retrieval.repositories.metadata_repository import MetadataRepository
from app.retrieval.config.settings import retrieval_settings
from app.retrieval.context.retrieval_context import RetrievalContext

logger = logging.getLogger(__name__)


class RetrievalManager:
    """The central brain coordinator supervising the full search query execution workflow."""

    def __init__(
        self,
        validator: RetrievalValidator,
        session_builder: RetrievalSessionBuilder,
        coordinator: RetrievalCoordinator,
        execution_manager: RetrievalExecutionManager,
        result_builder: RetrievalResultBuilder,
        telemetry_manager: TelemetryManager,
        query_processor: QueryProcessor,
        cache_manager: BaseCacheManager,
        retrieval_repository: RetrievalRepository,
        metadata_repository: MetadataRepository
    ):
        self.validator = validator
        self.session_builder = session_builder
        self.coordinator = coordinator
        self.execution_manager = execution_manager
        self.result_builder = result_builder
        self.telemetry_manager = telemetry_manager
        self.query_processor = query_processor
        self.cache_manager = cache_manager
        self.retrieval_repository = retrieval_repository
        self.metadata_repository = metadata_repository

    async def execute_retrieval(self, request_or_context: Union[RetrievalRequest, RetrievalContext]) -> RetrievalResponse:
        """Coordinated manager run cycle: validates query -> checks cache -> queries coordinator."""
        # 0. Ensure we are dealing with a RetrievalContext
        if isinstance(request_or_context, RetrievalContext):
            context = request_or_context
        else:
            from app.retrieval.context.context_factory import RetrievalContextFactory
            factory = RetrievalContextFactory(self.query_processor)
            context = factory.create_from_request(request_or_context)

        timeline = RetrievalTimelineMetrics()
        start_time = time.time()
        
        # 1. Initialize distributed tracing telemetry context
        trace_context = self.telemetry_manager.initialize_tracing(
            trace_id=context.tracing.trace_id,
            span_id=context.tracing.span_id,
            correlation_id=context.tracing.correlation_id
        )
        trace_id = trace_context["trace_id"]
        correlation_id = trace_context["correlation_id"]
        
        logger.info(
            f"[CorrelationID: {correlation_id}] [Retrieval Started] Query: '{context.query.original_query}' | "
            f"TraceID: {trace_id}"
        )
        
        # 2. Validate request parameters
        timeline.start_stage("validation")
        self.validator.validate(context)
        timeline.end_stage("validation")
        
        # 3. Build Session parameters
        session_details = self.session_builder.build_session(context)
        session_id = session_details["session_id"]
        self.execution_manager.update_state(session_id, f"initialized | TraceID: {trace_id}")
        
        # 4. Preprocess / Normalize Query (already normalized in query context)
        timeline.start_stage("normalization")
        normalized_query = context.query.normalized_query
        self.execution_manager.update_state(session_id, f"query_normalized | TraceID: {trace_id}")
        timeline.end_stage("normalization")
        
        # Verify access authorization constraints
        if context.metadata.document_scope:
            from uuid import UUID
            uuid_list = []
            for val in context.metadata.document_scope:
                try:
                    uuid_list.append(UUID(val) if isinstance(val, str) else val)
                except ValueError:
                    pass
            self.metadata_repository.verify_document_access(uuid_list)
            
        # 5. Check cache lookup
        timeline.start_stage("cache_lookup")
        limit = context.configuration.top_k
        threshold = context.configuration.similarity_threshold
        strategy_name = context.strategy.strategy_name
        
        cache_key = f"query:{normalized_query}:limit:{limit}:strat:{strategy_name}"
        cached_results = self.cache_manager.get(cache_key)
        timeline.end_stage("cache_lookup")
        
        if cached_results is not None:
            self.execution_manager.update_state(session_id, f"cache_hit | TraceID: {trace_id}")
            execution_time_ms = (time.time() - start_time) * 1000
            
            confidence = 0.0
            if cached_results:
                confidence = sum(r.score for r in cached_results) / len(cached_results)
                
            response_metadata = context.metadata.document_filters or {}
            response_metadata = {**response_metadata, **trace_context}
                
            logger.info(
                f"[CorrelationID: {correlation_id}] Cache HIT for query '{normalized_query}'"
            )
            return self.result_builder.build_response(
                query=normalized_query,
                results=cached_results,
                latency_ms=execution_time_ms,
                confidence=confidence,
                strategy=strategy_name,
                providers=["cache"],
                metadata=response_metadata,
                timeline=timeline.get_timeline(),
                context=context
            )

        # 6. Cache Miss, execute strategy retrieval
        self.execution_manager.update_state(session_id, f"searching | TraceID: {trace_id}")
        timeline.start_stage("search_execution")
        
        # Log span events
        self.telemetry_manager.instrument_provider_start("orchestrator", trace_context)
        
        logger.info(
            f"[CorrelationID: {correlation_id}] Cache MISS. Executing coordinator retrieve..."
        )
        items = await self.coordinator.retrieve(context)
        
        self.telemetry_manager.instrument_provider_end(
            provider_name="orchestrator", 
            tracing=trace_context, 
            duration_ms=(time.time() - start_time) * 1000
        )
        timeline.end_stage("search_execution")
        self.execution_manager.update_state(session_id, f"results_collected | TraceID: {trace_id}")

        # 7. Save cache index
        timeline.start_stage("caching")
        self.cache_manager.set(
            key=cache_key,
            value=items,
            ttl_seconds=retrieval_settings.CACHE_EXPIRATION_SECONDS
        )
        timeline.end_stage("caching")

        # 8. Log retrieval analytics
        self.retrieval_repository.log_search(
            query=normalized_query,
            strategy=strategy_name,
            result_count=len(items),
            latency_ms=(time.time() - start_time) * 1000,
            context=context
        )

        # Identify active source providers
        providers = []
        strat_lower = strategy_name.lower()
        if strat_lower == "semantic":
            providers = ["qdrant"]
        elif strat_lower == "keyword":
            providers = ["postgres"]
        else:
            providers = ["qdrant", "postgres"]

        if any("mock" in item.text_content.lower() for item in items):
            providers = ["mock"]

        # Calculate Confidence Score (e.g. average similarity ranking score)
        confidence = 0.0
        if items:
            confidence = sum(r.score for r in items) / len(items)

        # 9. Build response DTO contract
        self.execution_manager.update_state(session_id, f"completed | TraceID: {trace_id}")
        execution_time_ms = (time.time() - start_time) * 1000
        
        response_metadata = context.metadata.document_filters or {}
        response_metadata = {**response_metadata, **trace_context}
        
        logger.info(
            f"[CorrelationID: {correlation_id}] Retrieval completed in {execution_time_ms:.2f}ms"
        )
        return self.result_builder.build_response(
            query=normalized_query,
            results=items,
            latency_ms=execution_time_ms,
            confidence=confidence,
            strategy=strategy_name,
            providers=providers,
            metadata=response_metadata,
            timeline=timeline.get_timeline(),
            context=context
        )

