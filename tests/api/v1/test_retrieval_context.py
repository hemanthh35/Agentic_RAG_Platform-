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
