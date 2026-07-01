import pytest
from app.retrieval.context.context_builder import RetrievalContextBuilder
from app.retrieval.context.context_factory import RetrievalContextFactory
from app.retrieval.context.context_exceptions import ContextValidationError
from app.retrieval.schemas.query import RetrievalRequest
from app.retrieval.services.query_processor import QueryProcessor


def test_context_immutability():
    """Verify that any attribute mutation attempt on the frozen context raises exceptions."""
    builder = RetrievalContextBuilder()
    builder.with_query("hello search query", "hello search query")
    builder.with_providers(["qdrant"])
    context = builder.build()
    
    # Asserting Pydantic models are frozen read-only
    with pytest.raises(Exception):
        context.query.original_query = "modified search query"


def test_context_validation_checks():
    """Verify context structural validations check rules (e.g. negative timeout values)."""
    builder = RetrievalContextBuilder()
    builder.with_query("valid test query", "valid test query")
    builder.with_providers(["qdrant"])
    
    # Invalid negative timeout
    builder.with_config(top_k=10, threshold=0.5, timeout=-2.5)
    with pytest.raises(ContextValidationError) as exc_info:
        builder.build()
        
    assert "Timeout must be positive" in str(exc_info.value)


def test_context_factory_mapping():
    """Verify that RetrievalContextFactory parses API query requests correctly."""
    processor = QueryProcessor()
    factory = RetrievalContextFactory(processor)
    
    request = RetrievalRequest(
        query="  hello   tracing   queries  ",
        limit=7,
        strategy="keyword",
        correlation_id="corr-span-xyz-999"
    )
    
    context = factory.create_from_request(request)
    assert context.query.original_query == "  hello   tracing   queries  "
    assert context.query.normalized_query == "hello tracing queries"
    assert context.configuration.top_k == 7
    assert context.strategy.strategy_name == "keyword"
    assert context.tracing.correlation_id == "corr-span-xyz-999"


def test_context_extended_fields_propagation():
    """Verify that RetrievalContext supports the newly added extended fields for Part 2A."""
    builder = RetrievalContextBuilder()
    builder.with_query("semantic search engine", "semantic search engine", intent="fetch_info", query_type="code")
    builder.with_user(user_id="user-123", tenant_id="tenant-abc", role="developer")
    builder.with_providers(["qdrant"], preferred="qdrant", timeout=10.0, retry_count=5)
    builder.with_strategy("semantic", version="v2", ranking_policy="rrf")
    builder.with_tracing(correlation_id="corr-1234", trace_id="trace-abc", span_id="span-123", root_span="root-span-99")
    builder.with_execution(execution_id="exec-456", session_id="sess-789", deadline=1700000000.0, status="running")
    builder.with_metadata_context(collection_name="code_collection", search_domain="tech")
    
    context = builder.build()
    
    # Query Context checks
    assert context.query.original_query == "semantic search engine"
    assert context.query.intent == "fetch_info"
    assert context.query.query_type == "code"
    
    # User Context checks
    assert context.user.user_id == "user-123"
    assert context.user.tenant_id == "tenant-abc"
    assert context.user.role == "developer"
    
    # Provider Context checks
    assert context.provider.selected_providers == ["qdrant"]
    assert context.provider.preferred_provider == "qdrant"
    assert context.provider.provider_timeout == 10.0
    assert context.provider.provider_retry_count == 5
    
    # Strategy Context checks
    assert context.strategy.strategy_name == "semantic"
    assert context.strategy.strategy_version == "v2"
    assert context.strategy.ranking_policy == "rrf"
    
    # Tracing Context checks
    assert context.tracing.correlation_id == "corr-1234"
    assert context.tracing.root_span == "root-span-99"
    
    # Execution Context checks
    assert context.execution.execution_id == "exec-456"
    assert context.execution.session_id == "sess-789"
    assert context.execution.execution_deadline == 1700000000.0
    assert context.execution.execution_status == "running"
    
    # Metadata Context checks
    assert context.metadata.collection_name == "code_collection"
    assert context.metadata.search_domain == "tech"

