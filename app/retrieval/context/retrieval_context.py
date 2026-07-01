import time
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any


class RequestContext(BaseModel):
    """Sub-context carrying request lifecycle details."""
    model_config = ConfigDict(frozen=True)
    
    request_id: str = Field(..., description="Unique UUID tracking the incoming request")
    timestamp: float = Field(..., description="Epoch timestamp representing request initialization time")
    api_version: str = Field("v1", description="FastAPI API routing version")
    client_info: Optional[str] = Field(None, description="Optional metadata header regarding client environment")


class UserContext(BaseModel):
    """Sub-context carrying user identifiers and authorization rules."""
    model_config = ConfigDict(frozen=True)
    
    user_id: str = Field("anonymous", description="Unique identifier tracking user session actions")
    tenant_id: Optional[str] = Field(None, description="Optional tenant identifier for multi-tenant checks")
    org_id: Optional[str] = Field(None, description="Optional organization identifier for multi-tenant checks")
    role: Optional[str] = Field(None, description="Primary access role assigned to user")
    roles: List[str] = Field(default_factory=list, description="Access authorization roles assigned to user")
    permissions: List[str] = Field(default_factory=list, description="Explicit permissions granted to user")
    locale: Optional[str] = Field(None, description="Locale setting of the user")
    preferred_language: Optional[str] = Field(None, description="Preferred language for query results personalization")
    timezone: Optional[str] = Field(None, description="Timezone of the user")
    subscription_tier: Optional[str] = Field(None, description="Subscription tier of the user")


class QueryContext(BaseModel):
    """Sub-context carrying raw and cleaned user query keywords."""
    model_config = ConfigDict(frozen=True)
    
    original_query: str = Field(..., description="Raw query entered by the user")
    normalized_query: str = Field(..., description="Preprocessed query after whitespace compression")
    expanded_query: Optional[str] = Field(None, description="Optional query expanded version")
    detected_language: Optional[str] = Field(None, description="Optional detected language code")
    intent: Optional[str] = Field(None, description="Optional classified user intent")
    query_type: Optional[str] = Field(None, description="Optional classification (e.g. general, code, numeric)")
    token_count: Optional[int] = Field(None, description="Optional token count of the query")
    character_count: Optional[int] = Field(None, description="Optional character count of the query")
    query_timestamp: float = Field(default_factory=time.time, description="Timestamp when query was received/parsed")
    query_version: str = Field("v1", description="Version of the query context")
    query_language: str = Field("en", description="Target language code code indicator")


class ConfigurationContext(BaseModel):
    """Sub-context carrying thresholds, timeouts, and cache configurations."""
    model_config = ConfigDict(frozen=True)
    
    top_k: int = Field(10, description="Top-K limit boundaries parameter")
    similarity_threshold: float = Field(0.0, description="Similarity score cutoff threshold")
    timeout_sec: float = Field(5.0, description="Coordinated timeouts threshold limit")
    cache_enabled: bool = Field(True, description="Enable RAG cache lookups")
    retry_policy: Dict[str, Any] = Field(default_factory=dict, description="Retries and exponential backoff flags")
    feature_flags: Dict[str, bool] = Field(default_factory=dict, description="Operational search feature flags")


class ProviderContext(BaseModel):
    """Sub-context detailing connectors to invoke."""
    model_config = ConfigDict(frozen=True)
    
    selected_providers: List[str] = Field(..., description="List of target databases and API search systems")
    preferred_provider: Optional[str] = Field(None, description="Primary connector targeting priority queries")
    fallback_providers: List[str] = Field(default_factory=list, description="Sequence order fallbacks for circuit degraded paths")
    provider_options: Dict[str, Any] = Field(default_factory=dict, description="Connector specific parameters (e.g., Pinecone namespaces)")
    active_provider: Optional[str] = Field(None, description="Active provider currently running the search")
    provider_priority: Dict[str, int] = Field(default_factory=dict, description="Execution priority values for selected providers")
    provider_configuration: Dict[str, Any] = Field(default_factory=dict, description="Target configuration mapping for provider systems")
    provider_timeout: float = Field(5.0, description="Timeout limit specific to providers execution")
    provider_retry_count: int = Field(3, description="Maximum retry count allowed for providers calls")
    provider_capabilities: Dict[str, List[str]] = Field(default_factory=dict, description="Capabilities supported by each provider")
    provider_version: Dict[str, str] = Field(default_factory=dict, description="Software versions of active providers")
    provider_metadata: Dict[str, Any] = Field(default_factory=dict, description="Dynamic execution metadata for providers")


class StrategyContext(BaseModel):
    """Sub-context carrying search strategy modes."""
    model_config = ConfigDict(frozen=True)
    
    strategy_name: str = Field(..., description="Orchestration strategy (semantic, keyword, hybrid)")
    strategy_version: str = Field("v1", description="Orchestration strategy version identifier")
    strategy_configuration: Dict[str, Any] = Field(default_factory=dict, description="Configuration parameters for the active strategy")
    ranking_policy: str = Field("default", description="Aggregation sorting strategy")
    retrieval_mode: str = Field("standard", description="Search operation mode")
    search_policy: str = Field("default", description="Global search policy applied to retrieval strategy")
    feature_flags: Dict[str, bool] = Field(default_factory=dict, description="Feature flags specific to strategy execution")
    search_mode: str = Field("standard", description="Search operation mode (legacy compatibility)")
    ranking_strategy: str = Field("default", description="Aggregation sorting strategy (legacy compatibility)")


class TracingContext(BaseModel):
    """Sub-context carrying distributed tracing span parameters."""
    model_config = ConfigDict(frozen=True)
    
    correlation_id: str = Field(..., description="ID matching logs across services")
    trace_id: str = Field(..., description="Distributed tracing Span Parent Trace UUID")
    span_id: str = Field(..., description="Active execution block Span UUID")
    parent_span_id: Optional[str] = Field(None, description="Parent trace Span UUID if triggered from agent workflow")
    root_span: Optional[str] = Field(None, description="Root span descriptor or ID of the retrieval trace")
    execution_chain: List[str] = Field(default_factory=list, description="Sequence trace chain of executed components")
    trace_start_time: float = Field(default_factory=time.time, description="Distributed trace start time")


class ExecutionContext(BaseModel):
    """Sub-context carrying runtime state and execution tracking parameters."""
    model_config = ConfigDict(frozen=True)

    execution_id: str = Field(..., description="Unique ID for this specific context execution flow")
    request_id: str = Field(..., description="Request ID associated with the execution")
    session_id: Optional[str] = Field(None, description="Session ID associated with the execution")
    execution_start_time: float = Field(..., description="Epoch timestamp representing start of execution")
    execution_deadline: Optional[float] = Field(None, description="Epoch timestamp representing absolute deadline")
    execution_timeout: float = Field(5.0, description="Max execution duration allowed in seconds")
    current_stage: str = Field("created", description="Current step in retrieval pipeline lifecycle")
    retry_count: int = Field(0, description="Number of execution retries attempted so far")
    execution_status: str = Field("pending", description="Status indicator of the execution lifecycle")
    execution_priority: str = Field("normal", description="Priority level of execution (low, normal, high)")
    worker_id: Optional[str] = Field(None, description="Identifies the parallel background worker processing request")


class MetadataContext(BaseModel):
    """Sub-context carrying dynamic search scope metadata filters."""
    model_config = ConfigDict(frozen=True)

    collection_name: Optional[str] = Field(None, description="Target collection name matching search engine indexes")
    knowledge_base: Optional[str] = Field(None, description="Scope boundary limiting query to a specific knowledge base")
    document_scope: Optional[List[str]] = Field(None, description="Restricts chunk search to specified documents list")
    search_domain: Optional[str] = Field(None, description="Specific business/technical domain restriction")
    allowed_collections: List[str] = Field(default_factory=list, description="White-listed collections target can search")
    source_restrictions: Optional[Dict[str, Any]] = Field(None, description="Configured constraints limiting search sources")
    document_filters: Optional[Dict[str, Any]] = Field(None, description="Restricting filters mapped to documents fields")
    version_filters: Optional[Dict[str, Any]] = Field(None, description="Restricting filters mapped to document versions")
    metadata_filters: Optional[Dict[str, Any]] = Field(None, description="Restricting filters mapped to arbitrary chunk metadata fields")


class RetrievalContext(BaseModel):
    """Unified read-only data transport context carrying all parameters for search runs."""
    model_config = ConfigDict(frozen=True)
    
    request: RequestContext
    user: UserContext
    query: QueryContext
    configuration: ConfigurationContext
    provider: ProviderContext
    strategy: StrategyContext
    tracing: TracingContext
    execution: ExecutionContext
    metadata: MetadataContext

