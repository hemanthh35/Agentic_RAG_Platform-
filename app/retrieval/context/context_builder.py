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
    TracingContext,
    ExecutionContext,
    MetadataContext
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
        
        # User Context defaults
        self._user_id = "anonymous"
        self._tenant_id: Optional[str] = None
        self._org_id: Optional[str] = None
        self._role: Optional[str] = None
        self._roles: List[str] = []
        self._permissions: List[str] = []
        self._locale: Optional[str] = None
        self._preferred_language: Optional[str] = None
        self._timezone: Optional[str] = None
        self._subscription_tier: Optional[str] = None

        # Query Context defaults
        self._original_query = ""
        self._normalized_query = ""
        self._expanded_query: Optional[str] = None
        self._detected_language: Optional[str] = None
        self._intent: Optional[str] = None
        self._query_type: Optional[str] = None
        self._token_count: Optional[int] = None
        self._character_count: Optional[int] = None
        self._query_timestamp: float = self._timestamp
        self._query_version: str = "v1"
        self._query_language: str = "en"

        # Configuration Context defaults
        self._top_k = retrieval_settings.DEFAULT_RETRIEVAL_LIMIT
        self._similarity_threshold = retrieval_settings.DEFAULT_SIMILARITY_THRESHOLD
        self._timeout_sec = retrieval_settings.PROVIDER_TIMEOUT_SECONDS
        self._cache_enabled = True
        self._retry_policy: Dict[str, Any] = {}
        self._feature_flags: Dict[str, bool] = {}

        # Provider Context defaults
        self._selected_providers: List[str] = []
        self._preferred_provider: Optional[str] = None
        self._fallback_providers: List[str] = []
        self._provider_options: Dict[str, Any] = {}
        self._active_provider: Optional[str] = None
        self._provider_priority: Dict[str, int] = {}
        self._provider_configuration: Dict[str, Any] = {}
        self._provider_timeout: float = retrieval_settings.PROVIDER_TIMEOUT_SECONDS
        self._provider_retry_count: int = 3
        self._provider_capabilities: Dict[str, List[str]] = {}
        self._provider_version: Dict[str, str] = {}
        self._provider_metadata: Dict[str, Any] = {}

        # Strategy Context defaults
        self._strategy_name = "semantic"
        self._strategy_version: str = "v1"
        self._strategy_configuration: Dict[str, Any] = {}
        self._ranking_policy: str = "default"
        self._retrieval_mode: str = "standard"
        self._search_policy: str = "default"
        self._strategy_feature_flags: Dict[str, bool] = {}

        # Tracing Context defaults
        self._correlation_id = str(uuid4())
        self._trace_id = str(uuid4())
        self._span_id = str(uuid4())
        self._parent_span_id: Optional[str] = None
        self._root_span: Optional[str] = None
        self._execution_chain: List[str] = []
        self._trace_start_time: float = self._timestamp

        # Execution Context defaults
        self._execution_id = str(uuid4())
        self._session_id: Optional[str] = None
        self._execution_deadline: Optional[float] = None
        self._current_stage = "created"
        self._retry_count = 0
        self._execution_status = "pending"
        self._execution_priority = "normal"
        self._worker_id: Optional[str] = None

        # Metadata Context defaults
        self._collection_name: Optional[str] = None
        self._knowledge_base: Optional[str] = None
        self._document_scope: Optional[List[str]] = None
        self._search_domain: Optional[str] = None
        self._allowed_collections: List[str] = []
        self._source_restrictions: Optional[Dict[str, Any]] = None
        self._document_filters: Optional[Dict[str, Any]] = None
        self._version_filters: Optional[Dict[str, Any]] = None
        self._metadata_filters: Optional[Dict[str, Any]] = None

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
        roles: Optional[List[str]] = None,
        tenant_id: Optional[str] = None,
        role: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        locale: Optional[str] = None,
        preferred_language: Optional[str] = None,
        timezone: Optional[str] = None,
        subscription_tier: Optional[str] = None
    ) -> "RetrievalContextBuilder":
        """Assign user authorization identifier context parameters."""
        self._user_id = user_id
        self._org_id = org_id
        if roles:
            self._roles = roles
        if tenant_id:
            self._tenant_id = tenant_id
        if role:
            self._role = role
        if permissions:
            self._permissions = permissions
        if locale:
            self._locale = locale
        if preferred_language:
            self._preferred_language = preferred_language
        if timezone:
            self._timezone = timezone
        if subscription_tier:
            self._subscription_tier = subscription_tier
        return self

    def with_query(
        self,
        query: str,
        normalized: str,
        expanded: Optional[str] = None,
        detected_language: Optional[str] = None,
        intent: Optional[str] = None,
        query_type: Optional[str] = None,
        token_count: Optional[int] = None,
        character_count: Optional[int] = None,
        query_timestamp: Optional[float] = None,
        query_version: str = "v1",
        query_language: str = "en"
    ) -> "RetrievalContextBuilder":
        """Assign request original query parameters."""
        self._original_query = query
        self._normalized_query = normalized
        self._expanded_query = expanded
        self._detected_language = detected_language
        self._intent = intent
        self._query_type = query_type
        self._token_count = token_count
        self._character_count = character_count
        if query_timestamp:
            self._query_timestamp = query_timestamp
        self._query_version = query_version
        self._query_language = query_language
        return self

    def with_config(
        self,
        top_k: int,
        threshold: float,
        timeout: float,
        cache_enabled: bool = True,
        retry_policy: Optional[Dict[str, Any]] = None,
        feature_flags: Optional[Dict[str, bool]] = None
    ) -> "RetrievalContextBuilder":
        """Assign execution thresholds parameter configs."""
        self._top_k = top_k
        self._similarity_threshold = threshold
        self._timeout_sec = timeout
        self._cache_enabled = cache_enabled
        if retry_policy:
            self._retry_policy = retry_policy
        if feature_flags:
            self._feature_flags = feature_flags
        return self

    def with_providers(
        self,
        selected: List[str],
        preferred: Optional[str] = None,
        fallbacks: Optional[List[str]] = None,
        options: Optional[Dict[str, Any]] = None,
        active: Optional[str] = None,
        priority: Optional[Dict[str, int]] = None,
        configuration: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        retry_count: Optional[int] = None,
        capabilities: Optional[Dict[str, List[str]]] = None,
        version: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "RetrievalContextBuilder":
        """Assign database providers catalog list to query."""
        self._selected_providers = selected
        self._preferred_provider = preferred
        if fallbacks:
            self._fallback_providers = fallbacks
        if options:
            self._provider_options = options
        self._active_provider = active
        if priority:
            self._provider_priority = priority
        if configuration:
            self._provider_configuration = configuration
        if timeout is not None:
            self._provider_timeout = timeout
        if retry_count is not None:
            self._provider_retry_count = retry_count
        if capabilities:
            self._provider_capabilities = capabilities
        if version:
            self._provider_version = version
        if metadata:
            self._provider_metadata = metadata
        return self

    def with_strategy(
        self,
        strategy: str,
        version: str = "v1",
        configuration: Optional[Dict[str, Any]] = None,
        ranking_policy: str = "default",
        retrieval_mode: str = "standard",
        search_policy: str = "default",
        feature_flags: Optional[Dict[str, bool]] = None
    ) -> "RetrievalContextBuilder":
        """Assign search routing orchestration strategy."""
        self._strategy_name = strategy
        self._strategy_version = version
        if configuration:
            self._strategy_configuration = configuration
        self._ranking_policy = ranking_policy
        self._retrieval_mode = retrieval_mode
        self._search_policy = search_policy
        if feature_flags:
            self._strategy_feature_flags = feature_flags
        return self

    def with_tracing(
        self,
        correlation_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        root_span: Optional[str] = None,
        execution_chain: Optional[List[str]] = None,
        trace_start_time: Optional[float] = None
    ) -> "RetrievalContextBuilder":
        """Assign distributed OpenTelemetry tracing parameters."""
        if correlation_id:
            self._correlation_id = correlation_id
        if trace_id:
            self._trace_id = trace_id
        if span_id:
            self._span_id = span_id
        self._parent_span_id = parent_span_id
        self._root_span = root_span
        if execution_chain:
            self._execution_chain = execution_chain
        if trace_start_time:
            self._trace_start_time = trace_start_time
        return self

    def with_execution(
        self,
        execution_id: Optional[str] = None,
        session_id: Optional[str] = None,
        deadline: Optional[float] = None,
        timeout: Optional[float] = None,
        stage: str = "created",
        retry_count: int = 0,
        status: str = "pending",
        priority: str = "normal",
        worker_id: Optional[str] = None
    ) -> "RetrievalContextBuilder":
        """Assign execution lifecycle variables."""
        if execution_id:
            self._execution_id = execution_id
        if session_id:
            self._session_id = session_id
        self._execution_deadline = deadline
        if timeout is not None:
            self._timeout_sec = timeout
        self._current_stage = stage
        self._retry_count = retry_count
        self._execution_status = status
        self._execution_priority = priority
        self._worker_id = worker_id
        return self

    def with_metadata(self, metadata: Dict[str, Any]) -> "RetrievalContextBuilder":
        """Assign custom metadata filter fields for legacy compatibility."""
        if "collection_name" in metadata:
            self._collection_name = metadata["collection_name"]
        if "knowledge_base" in metadata:
            self._knowledge_base = metadata["knowledge_base"]
        if "document_scope" in metadata:
            self._document_scope = metadata["document_scope"]
        if "search_domain" in metadata:
            self._search_domain = metadata["search_domain"]
        if "allowed_collections" in metadata:
            self._allowed_collections = metadata["allowed_collections"]
        if "source_restrictions" in metadata:
            self._source_restrictions = metadata["source_restrictions"]
        if "document_filters" in metadata:
            self._document_filters = metadata["document_filters"]
        if "version_filters" in metadata:
            self._version_filters = metadata["version_filters"]
        if "metadata_filters" in metadata:
            self._metadata_filters = metadata["metadata_filters"]
        return self

    def with_metadata_context(
        self,
        collection_name: Optional[str] = None,
        knowledge_base: Optional[str] = None,
        document_scope: Optional[List[str]] = None,
        search_domain: Optional[str] = None,
        allowed_collections: Optional[List[str]] = None,
        source_restrictions: Optional[Dict[str, Any]] = None,
        document_filters: Optional[Dict[str, Any]] = None,
        version_filters: Optional[Dict[str, Any]] = None,
        metadata_filters: Optional[Dict[str, Any]] = None
    ) -> "RetrievalContextBuilder":
        """Assign custom request execution tags with precise schema details."""
        self._collection_name = collection_name
        self._knowledge_base = knowledge_base
        self._document_scope = document_scope
        self._search_domain = search_domain
        if allowed_collections:
            self._allowed_collections = allowed_collections
        self._source_restrictions = source_restrictions
        self._document_filters = document_filters
        self._version_filters = version_filters
        self._metadata_filters = metadata_filters
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
                tenant_id=self._tenant_id,
                org_id=self._org_id,
                role=self._role,
                roles=self._roles,
                permissions=self._permissions,
                locale=self._locale,
                preferred_language=self._preferred_language,
                timezone=self._timezone,
                subscription_tier=self._subscription_tier
            ),
            query=QueryContext(
                original_query=self._original_query,
                normalized_query=self._normalized_query,
                expanded_query=self._expanded_query,
                detected_language=self._detected_language,
                intent=self._intent,
                query_type=self._query_type,
                token_count=self._token_count,
                character_count=self._character_count,
                query_timestamp=self._query_timestamp,
                query_version=self._query_version,
                query_language=self._query_language
            ),
            configuration=ConfigurationContext(
                top_k=self._top_k,
                similarity_threshold=self._similarity_threshold,
                timeout_sec=self._timeout_sec,
                cache_enabled=self._cache_enabled,
                retry_policy=self._retry_policy,
                feature_flags=self._feature_flags
            ),
            provider=ProviderContext(
                selected_providers=self._selected_providers,
                preferred_provider=self._preferred_provider,
                fallback_providers=self._fallback_providers,
                provider_options=self._provider_options,
                active_provider=self._active_provider,
                provider_priority=self._provider_priority,
                provider_configuration=self._provider_configuration,
                provider_timeout=self._provider_timeout,
                provider_retry_count=self._provider_retry_count,
                provider_capabilities=self._provider_capabilities,
                provider_version=self._provider_version,
                provider_metadata=self._provider_metadata
            ),
            strategy=StrategyContext(
                strategy_name=self._strategy_name,
                strategy_version=self._strategy_version,
                strategy_configuration=self._strategy_configuration,
                ranking_policy=self._ranking_policy,
                retrieval_mode=self._retrieval_mode,
                search_policy=self._search_policy,
                feature_flags=self._strategy_feature_flags,
                search_mode=self._retrieval_mode,
                ranking_strategy=self._ranking_policy
            ),
            tracing=TracingContext(
                correlation_id=self._correlation_id,
                trace_id=self._trace_id,
                span_id=self._span_id,
                parent_span_id=self._parent_span_id,
                root_span=self._root_span,
                execution_chain=self._execution_chain,
                trace_start_time=self._trace_start_time
            ),
            execution=ExecutionContext(
                execution_id=self._execution_id,
                request_id=self._request_id,
                session_id=self._session_id,
                execution_start_time=self._timestamp,
                execution_deadline=self._execution_deadline,
                execution_timeout=self._timeout_sec,
                current_stage=self._current_stage,
                retry_count=self._retry_count,
                execution_status=self._execution_status,
                execution_priority=self._execution_priority,
                worker_id=self._worker_id
            ),
            metadata=MetadataContext(
                collection_name=self._collection_name,
                knowledge_base=self._knowledge_base,
                document_scope=self._document_scope,
                search_domain=self._search_domain,
                allowed_collections=self._allowed_collections,
                source_restrictions=self._source_restrictions,
                document_filters=self._document_filters,
                version_filters=self._version_filters,
                metadata_filters=self._metadata_filters
            )
        )
        
        self.validator.validate(context)
        return context

