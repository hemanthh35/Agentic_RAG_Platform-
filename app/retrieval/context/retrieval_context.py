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
    org_id: Optional[str] = Field(None, description="Optional organization identifier for multi-tenant checks")
    roles: List[str] = Field(default_factory=list, description="Access authorization roles assigned to user")


class QueryContext(BaseModel):
    """Sub-context carrying raw and cleaned user query keywords."""
    model_config = ConfigDict(frozen=True)
    
    original_query: str = Field(..., description="Raw query entered by the user")
    normalized_query: str = Field(..., description="Preprocessed query after whitespace compression")
    query_type: Optional[str] = Field(None, description="Optional classification (e.g. general, code, numeric)")
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


class StrategyContext(BaseModel):
    """Sub-context carrying search strategy modes."""
    model_config = ConfigDict(frozen=True)
    
    strategy_name: str = Field(..., description="Orchestration strategy (semantic, keyword, hybrid)")
    search_mode: str = Field("standard", description="Search operation mode")
    ranking_strategy: str = Field("default", description="Aggregation sorting strategy")


class TracingContext(BaseModel):
    """Sub-context carrying distributed tracing span parameters."""
    model_config = ConfigDict(frozen=True)
    
    correlation_id: str = Field(..., description="ID matching logs across services")
    trace_id: str = Field(..., description="Distributed tracing Span Parent Trace UUID")
    span_id: str = Field(..., description="Active execution block Span UUID")
    parent_span_id: Optional[str] = Field(None, description="Parent trace Span UUID if triggered from agent workflow")


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
    execution: Dict[str, Any] = Field(default_factory=dict, description="Dynamic execution stats")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="General key-value parameters")
