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
        
        # Map Query Context
        char_count = len(request.query)
        word_count = len(request.query.split())
        builder.with_query(
            query=request.query,
            normalized=normalized,
            query_type=request.search_type,
            character_count=char_count,
            token_count=word_count  # Simple approximation
        )
        
        # Map Configuration Context
        builder.with_config(
            top_k=limit,
            threshold=threshold,
            timeout=retrieval_settings.PROVIDER_TIMEOUT_SECONDS,
            cache_enabled=True,
            feature_flags={}
        )
        
        # Map Provider Context
        options = request.options or {}
        builder.with_providers(
            selected=providers,
            options=options,
            timeout=retrieval_settings.PROVIDER_TIMEOUT_SECONDS
        )
        
        # Map Strategy Context
        builder.with_strategy(
            strategy=request.strategy,
            configuration=options
        )
        
        # Map Request Context
        if request.session_id:
            builder.with_request(request_id=request.session_id)
            
        # Map User Context
        if request.user_id:
            builder.with_user(user_id=str(request.user_id))
            
        # Map Tracing Context
        builder.with_tracing(
            correlation_id=request.correlation_id,
            trace_id=request.trace_id,
            span_id=request.span_id
        )
        
        # Map Execution Context (which will be built inside builder)
        if request.session_id:
            builder.with_execution(
                session_id=request.session_id,
                timeout=retrieval_settings.PROVIDER_TIMEOUT_SECONDS
            )
        
        # Map Metadata Context
        document_scope = None
        if request.filters and "document_id" in request.filters:
            doc_ids = request.filters["document_id"]
            if isinstance(doc_ids, list):
                document_scope = [str(d) for d in doc_ids]
            else:
                document_scope = [str(doc_ids)]

        builder.with_metadata_context(
            collection_name=request.collection,
            document_scope=document_scope,
            document_filters=request.filters,
            metadata_filters=request.filters
        )
        
        if request.metadata:
            builder.with_metadata(request.metadata)
            
        return builder.build()

