import pytest
from app.retrieval.dependencies.dependencies import get_retrieval_service
from app.retrieval.schemas.query import RetrievalRequest


@pytest.mark.asyncio
async def test_retrieval_manager_direct_execution():
    """Verify that RetrievalManager coordinates query execution and yields timeline metrics."""
    service = get_retrieval_service()
    manager = service.manager
    
    request = RetrievalRequest(
        query="test execution queries",
        limit=2,
        strategy="hybrid"
    )
    
    response = await manager.execute_retrieval(request)
    assert response.query == "test execution queries"
    assert len(response.results) > 0
    assert response.search_strategy == "hybrid"
    
    # Verify timeline tracking was recorded in metadata
    assert "execution_timeline_ms" in response.metadata
    timeline = response.metadata["execution_timeline_ms"]
    assert "validation" in timeline
    assert "normalization" in timeline
    assert "search_execution" in timeline
