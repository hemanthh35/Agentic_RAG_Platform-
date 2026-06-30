import time
from uuid import uuid4
from typing import Dict, Any, List, Optional

from app.retrieval.context.retrieval_context import (
    RetrievalContext,
    RequestContext,
    UserContext,
    QueryContext,
    ConfigurationContext,
    ProviderContext,
    StrategyContext,
    TracingContext
)
from app.retrieval.context.context_validator import RetrievalContextValidator
from app.retrieval.config.settings import retrieval_settings


class RetrievalContextBuilder:
    """Assembles and constructs immutable RetrievalContext instances."""

    def __init__(self, validator: Optional[RetrievalContextValidator] = None):
        self.validator = validator or RetrievalContextValidator()
        self._request_id = str(uuid4())
        self._timestamp = time.time()
        self._client_info: Optional[str] = None
        self._user_id = "anonymous"
        self._org_id: Optional[str] = None
        self._roles: List[str] = []
        self._original_query = ""
        self._normalized_query = ""
        self._top_k = retrieval_settings.DEFAULT_RETRIEVAL_LIMIT
        self._similarity_threshold = retrieval_settings.DEFAULT_SIMILARITY_THRESHOLD
        self._timeout_sec = retrieval_settings.PROVIDER_TIMEOUT_SECONDS
        self._cache_enabled = True
        self._selected_providers: List[str] = []
        self._strategy_name = "semantic"
        self._correlation_id = str(uuid4())
        self._trace_id = str(uuid4())
        self._span_id = str(uuid4())
        self._parent_span_id: Optional[str] = None
        self._metadata: Dict[str, Any] = {}

    def with_request(
        self,
        request_id: Optional[str] = None,
        client_info: Optional[str] = None
    ) -> "RetrievalContextBuilder":
        """Assign request tracing credentials and tags."""
        if request_id:
            self._request_id = request_id
        self._client_info = client_info
        return self

    def with_user(
        self,
        user_id: str,
        org_id: Optional[str] = None,
        roles: Optional[List[str]] = None
    ) -> "RetrievalContextBuilder":
        """Assign user authorization identifier context parameters."""
        self._user_id = user_id
        self._org_id = org_id
        if roles:
            self._roles = roles
        return self

    def with_query(self, query: str, normalized: str) -> "RetrievalContextBuilder":
        """Assign request original query parameters."""
        self._original_query = query
        self._normalized_query = normalized
        return self

    def with_config(
        self,
        top_k: int,
        threshold: float,
        timeout: float,
        cache_enabled: bool = True
    ) -> "RetrievalContextBuilder":
        """Assign execution thresholds parameter configs."""
        self._top_k = top_k
        self._similarity_threshold = threshold
        self._timeout_sec = timeout
        self._cache_enabled = cache_enabled
        return self

    def with_providers(self, selected: List[str]) -> "RetrievalContextBuilder":
        """Assign database providers catalog list to query."""
        self._selected_providers = selected
        return self

    def with_strategy(self, strategy: str) -> "RetrievalContextBuilder":
        """Assign search routing orchestration strategy."""
        self._strategy_name = strategy
        return self

    def with_tracing(
        self,
        correlation_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        parent_span_id: Optional[str] = None
    ) -> "RetrievalContextBuilder":
        """Assign distributed OpenTelemetry tracing parameters."""
        if correlation_id:
            self._correlation_id = correlation_id
        if trace_id:
            self._trace_id = trace_id
        if span_id:
            self._span_id = span_id
        self._parent_span_id = parent_span_id
        return self

    def with_metadata(self, metadata: Dict[str, Any]) -> "RetrievalContextBuilder":
        """Assign custom request execution tags."""
        self._metadata.update(metadata)
        return self

    def build(self) -> RetrievalContext:
        """Construct the frozen RetrievalContext object and run validation check rules."""
        if not self._selected_providers:
            strat = self._strategy_name.lower()
            if strat == "semantic":
                self._selected_providers = ["qdrant"]
            elif strat == "keyword":
                self._selected_providers = ["postgres"]
            else:
                self._selected_providers = ["qdrant", "postgres"]

        context = RetrievalContext(
            request=RequestContext(
                request_id=self._request_id,
                timestamp=self._timestamp,
                client_info=self._client_info
            ),
            user=UserContext(
                user_id=self._user_id,
                org_id=self._org_id,
                roles=self._roles
            ),
            query=QueryContext(
                original_query=self._original_query,
                normalized_query=self._normalized_query
            ),
            configuration=ConfigurationContext(
                top_k=self._top_k,
                similarity_threshold=self._similarity_threshold,
                timeout_sec=self._timeout_sec,
                cache_enabled=self._cache_enabled
            ),
            provider=ProviderContext(
                selected_providers=self._selected_providers
            ),
            strategy=StrategyContext(
                strategy_name=self._strategy_name
            ),
            tracing=TracingContext(
                correlation_id=self._correlation_id,
                trace_id=self._trace_id,
                span_id=self._span_id,
                parent_span_id=self._parent_span_id
            ),
            metadata=self._metadata
        )
        
        self.validator.validate(context)
        return context
