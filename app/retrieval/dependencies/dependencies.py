from app.retrieval.providers.providers import (
    QdrantRetrievalProvider,
    PostgresRetrievalProvider,
    MockRetrievalProvider
)
from app.retrieval.strategies.strategies import (
    SemanticRetrievalStrategy,
    KeywordRetrievalStrategy,
    HybridRetrievalStrategy
)
from app.retrieval.orchestrator.orchestrator import RetrievalOrchestrator
from app.retrieval.services.retrieval_service import RetrievalService


def get_retrieval_service() -> RetrievalService:
    """Dependency Injection provider tree constructing and resolving the RetrievalService hierarchy."""
    # 1. Instantiate low-level infrastructure providers
    qdrant_provider = QdrantRetrievalProvider()
    postgres_provider = PostgresRetrievalProvider()
    mock_provider = MockRetrievalProvider()
    
    providers = [qdrant_provider, postgres_provider, mock_provider]
    
    # 2. Instantiate strategies, composing them with injected providers
    semantic_strategy = SemanticRetrievalStrategy(providers)
    keyword_strategy = KeywordRetrievalStrategy(providers)
    hybrid_strategy = HybridRetrievalStrategy(providers)
    
    strategies = [semantic_strategy, keyword_strategy, hybrid_strategy]
    
    # 3. Instantiate orchestrator, composing it with injected strategies
    orchestrator = RetrievalOrchestrator(strategies)
    
    # 4. Return high-level service orchestrator
    return RetrievalService(orchestrator)
