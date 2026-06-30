from app.retrieval.schemas.query import RetrievalRequest
from app.retrieval.context.retrieval_context import RetrievalContext
from app.retrieval.context.context_builder import RetrievalContextBuilder
from app.retrieval.services.query_processor import QueryProcessor
from app.retrieval.config.settings import retrieval_settings


class RetrievalContextFactory:
    """Factory initializing and mapping RetrievalContext instances from search request DTO payload objects."""

    def __init__(self, query_processor: QueryProcessor):
        self.query_processor = query_processor

    def create_from_request(self, request: RetrievalRequest) -> RetrievalContext:
        """Parse incoming request schema options and return initialized, validated RetrievalContext."""
        normalized = self.query_processor.preprocess(request.query)
        
        limit = request.limit if request.limit else retrieval_settings.DEFAULT_RETRIEVAL_LIMIT
        threshold = request.threshold if request.threshold is not None else retrieval_settings.DEFAULT_SIMILARITY_THRESHOLD
        
        # Deduce database providers scope
        providers = []
        strat = request.strategy.lower()
        if strat == "semantic":
            providers = ["qdrant"]
        elif strat == "keyword":
            providers = ["postgres"]
        else:
            providers = ["qdrant", "postgres"]

        builder = RetrievalContextBuilder()
        builder.with_query(request.query, normalized)
        builder.with_config(
            top_k=limit,
            threshold=threshold,
            timeout=retrieval_settings.PROVIDER_TIMEOUT_SECONDS,
            cache_enabled=True
        )
        builder.with_providers(providers)
        builder.with_strategy(request.strategy)
        
        if request.session_id:
            builder.with_request(request_id=request.session_id)
        if request.user_id:
            builder.with_user(user_id=str(request.user_id))
            
        builder.with_tracing(
            correlation_id=request.correlation_id,
            trace_id=request.trace_id,
            span_id=request.span_id
        )
        
        if request.metadata:
            builder.with_metadata(request.metadata)
            
        return builder.build()
