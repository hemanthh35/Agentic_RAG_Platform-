import time
import logging
from typing import List, Dict, Any, Optional
from uuid import uuid4

from app.retrieval.interfaces.service_interface import BaseRetrievalService
from app.retrieval.orchestrator.retrieval_orchestrator import RetrievalOrchestrator
from app.retrieval.services.validation_service import ValidationService
from app.retrieval.services.context_service import ContextService
from app.retrieval.services.query_processor import QueryProcessor
from app.retrieval.services.metrics_service import MetricsService
from app.retrieval.cache.cache_manager import BaseCacheManager
from app.retrieval.repositories.retrieval_repository import RetrievalRepository
from app.retrieval.repositories.metadata_repository import MetadataRepository
from app.retrieval.schemas.query import RetrievalRequest, RetrievalResponse, RetrievalResultItem
from app.retrieval.config.settings import retrieval_settings

logger = logging.getLogger(__name__)


class RetrievalService(BaseRetrievalService):
    """Stateless high-level service coordinating the full search retrieval lifecycle."""

    def __init__(
        self,
        orchestrator: RetrievalOrchestrator,
        validation_service: ValidationService,
        context_service: ContextService,
        query_processor: QueryProcessor,
        metrics_service: MetricsService,
        cache_manager: BaseCacheManager,
        retrieval_repository: RetrievalRepository,
        metadata_repository: MetadataRepository
    ):
        self.orchestrator = orchestrator
        self.validation_service = validation_service
        self.context_service = context_service
        self.query_processor = query_processor
        self.metrics_service = metrics_service
        self.cache_manager = cache_manager
        self.retrieval_repository = retrieval_repository
        self.metadata_repository = metadata_repository

    async def retrieve_context(self, request: RetrievalRequest) -> RetrievalResponse:
        """Coordinated retrieval run cycle: validates parameters -> strips query -> triggers search."""
        start_time = time.time()
        logger.info("API Request received for query search.")
        
        try:
            # 1. Validate Query
            query_raw = request.query
            query_text = self.validation_service.validate_request_query(query_raw)
            
            limit = request.limit if request.limit else retrieval_settings.DEFAULT_RETRIEVAL_LIMIT
            threshold = request.threshold if request.threshold is not None else retrieval_settings.DEFAULT_SIMILARITY_THRESHOLD
            
            self.validation_service.validate_parameters(limit, threshold)
            
            # 2. Normalize / Preprocess Query
            normalized_query = self.query_processor.preprocess(query_text)
            logger.info(f"Query normalized: '{normalized_query}'")

            # Verify document permissions if doc filters exist
            if request.filters and "document_id" in request.filters:
                from uuid import UUID
                doc_ids = request.filters["document_id"]
                if not isinstance(doc_ids, list):
                    doc_ids = [doc_ids]
                
                uuid_list = []
                for val in doc_ids:
                    try:
                        uuid_list.append(UUID(val) if isinstance(val, str) else val)
                    except ValueError:
                        pass
                self.metadata_repository.verify_document_access(uuid_list)

            # 3. Create Retrieval Context & Session
            session_id = request.session_id if request.session_id else str(uuid4())
            logger.info(f"Initialized retrieval session: {session_id}")

            # 4. Check Cache
            cache_key = f"query:{normalized_query}:limit:{limit}:strat:{request.strategy}"
            cached_results = self.cache_manager.get(cache_key)
            if cached_results is not None:
                logger.info(f"Retrieval Cache HIT for key: {cache_key}")
                execution_time_ms = (time.time() - start_time) * 1000
                self.metrics_service.record_query(execution_time_ms, cache_hit=True, success=True)
                
                # Confidence Calculation (average score of hits)
                confidence = 0.0
                if cached_results:
                    confidence = sum(r.score for r in cached_results) / len(cached_results)
                    
                return self._build_response_object(
                    query=normalized_query,
                    results=cached_results,
                    latency_ms=execution_time_ms,
                    confidence=confidence,
                    strategy=request.strategy,
                    providers=["cache"],
                    metadata=request.metadata
                )

            logger.info(f"Retrieval Cache MISS for key: {cache_key}")

            # 5. Execute Retrieval (Orchestrated Strategy & Pipeline)
            items = await self.orchestrator.execute_retrieval(
                query=normalized_query,
                limit=limit,
                threshold=threshold,
                strategy_name=request.strategy,
                filters=request.filters
            )

            # 6. Validate Results (dedup, latency metrics, save to cache)
            execution_time_ms = (time.time() - start_time) * 1000
            self.metrics_service.record_query(execution_time_ms, cache_hit=False, success=True)

            self.cache_manager.set(
                key=cache_key,
                value=items,
                ttl_seconds=retrieval_settings.CACHE_EXPIRATION_SECONDS
            )

            # Log to Repository database analytics
            self.retrieval_repository.log_search(
                query=normalized_query,
                strategy=request.strategy,
                result_count=len(items),
                latency_ms=execution_time_ms
            )

            # Attribute queried providers
            providers = []
            strat_lower = request.strategy.lower()
            if strat_lower == "semantic":
                providers = ["qdrant"]
            elif strat_lower == "keyword":
                providers = ["postgres"]
            else:
                providers = ["qdrant", "postgres"]

            if any("mock" in item.text_content.lower() for item in items):
                providers = ["mock"]

            # Calculate Confidence Score (e.g., average similarity ranking score)
            confidence = 0.0
            if items:
                confidence = sum(r.score for r in items) / len(items)

            # 7. Build Retrieval Result & Return Response
            return self._build_response_object(
                query=normalized_query,
                results=items,
                latency_ms=execution_time_ms,
                confidence=confidence,
                strategy=request.strategy,
                providers=providers,
                metadata=request.metadata
            )
            
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            self.metrics_service.record_query(execution_time_ms, cache_hit=False, success=False)
            logger.error(f"Search retrieval pipeline failed: {e}")
            raise

    def _build_response_object(
        self,
        query: str,
        results: List[RetrievalResultItem],
        latency_ms: float,
        confidence: float,
        strategy: str,
        providers: List[str],
        metadata: Optional[Dict[str, Any]]
    ) -> RetrievalResponse:
        """Construct the comprehensive RetrievalResponse contract object."""
        provider_stats = {
            p: {"latency_ms": round(latency_ms / len(providers) if providers else latency_ms, 2)}
            for p in providers
        }
        
        return RetrievalResponse(
            query=query,
            results=results,
            retrieved_chunks=results,
            items=results,
            search_time_ms=round(latency_ms, 2),
            execution_time_ms=round(latency_ms, 2),
            confidence_score=round(confidence, 4),
            search_strategy=strategy,
            strategy_used=strategy,
            metadata=metadata,
            provider_information=provider_stats,
            total_results=len(results),
            providers_queried=providers
        )
