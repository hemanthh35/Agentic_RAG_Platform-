from app.retrieval.providers.mock_provider import MockRetrievalProvider
from app.retrieval.providers.qdrant_provider import QdrantRetrievalProvider
from app.retrieval.providers.postgres_provider import PostgresRetrievalProvider
from app.retrieval.providers.registry import provider_registry

from app.retrieval.strategies.semantic_strategy import SemanticRetrievalStrategy
from app.retrieval.strategies.keyword_strategy import KeywordRetrievalStrategy
from app.retrieval.strategies.hybrid_strategy import HybridRetrievalStrategy

from app.retrieval.orchestrator.retrieval_orchestrator import RetrievalOrchestrator
from app.retrieval.services.retrieval_service import RetrievalService
from app.retrieval.services.validation_service import ValidationService
from app.retrieval.services.context_service import ContextService
from app.retrieval.cache.cache_manager import InMemoryCacheManager
from app.retrieval.repositories.retrieval_repository import RetrievalRepository
from app.retrieval.repositories.metadata_repository import MetadataRepository

# Initialize singleton instances for providers to avoid multiple registration warnings
_mock_provider = MockRetrievalProvider()
_qdrant_provider = QdrantRetrievalProvider()
_postgres_provider = PostgresRetrievalProvider()

# Register providers to registry catalog
provider_registry.register_provider(_mock_provider)
provider_registry.register_provider(_qdrant_provider)
provider_registry.register_provider(_postgres_provider)

# Cache manager singleton
_cache_manager = InMemoryCacheManager()

# Validation & Context services singletons
_validation_service = ValidationService()
_context_service = ContextService()

# Repositories singletons
_retrieval_repo = RetrievalRepository()
_metadata_repo = MetadataRepository()


def get_retrieval_service() -> RetrievalService:
    """Dependency Injection provider tree constructing and resolving the RetrievalService hierarchy."""
    # Resolve providers list from registry
    providers = [
        provider_registry.get_provider("qdrant"),
        provider_registry.get_provider("postgres"),
        provider_registry.get_provider("mock")
    ]
    
    # Instantiate search strategies
    semantic_strategy = SemanticRetrievalStrategy(providers)
    keyword_strategy = KeywordRetrievalStrategy(providers)
    hybrid_strategy = HybridRetrievalStrategy(providers)
    
    strategies = [semantic_strategy, keyword_strategy, hybrid_strategy]
    
    # Instantiate orchestrator
    orchestrator = RetrievalOrchestrator(strategies)
    
    # Return high-level coordinate service
    return RetrievalService(
        orchestrator=orchestrator,
        validation_service=_validation_service,
        context_service=_context_service,
        cache_manager=_cache_manager,
        retrieval_repository=_retrieval_repo
    )
