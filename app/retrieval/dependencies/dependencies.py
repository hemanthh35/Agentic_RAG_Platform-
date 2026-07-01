from app.retrieval.providers.mock_provider import MockRetrievalProvider
from app.retrieval.providers.qdrant_provider import QdrantRetrievalProvider
from app.retrieval.providers.postgres_provider import PostgresRetrievalProvider
from app.retrieval.providers.registry import provider_registry

from app.retrieval.strategies.semantic_strategy import SemanticRetrievalStrategy
from app.retrieval.strategies.keyword_strategy import KeywordRetrievalStrategy
from app.retrieval.strategies.hybrid_strategy import HybridRetrievalStrategy

from app.retrieval.orchestrator.pipeline import RetrievalPipeline
from app.retrieval.orchestrator.retrieval_orchestrator import RetrievalOrchestrator
from app.retrieval.services.retrieval_service import RetrievalService
from app.retrieval.services.validation_service import ValidationService
from app.retrieval.services.context_service import ContextService
from app.retrieval.services.query_processor import QueryProcessor
from app.retrieval.services.metrics_service import MetricsService
from app.retrieval.cache.cache_manager import InMemoryCacheManager
from app.retrieval.repositories.retrieval_repository import RetrievalRepository
from app.retrieval.repositories.metadata_repository import MetadataRepository

# Import Retrieval Manager components
from app.retrieval.manager.validator import RetrievalValidator
from app.retrieval.manager.session_builder import RetrievalSessionBuilder
from app.retrieval.manager.coordinator import RetrievalCoordinator
from app.retrieval.manager.execution_manager import RetrievalExecutionManager
from app.retrieval.manager.result_builder import RetrievalResultBuilder
from app.retrieval.manager.circuit_breaker import ProviderCircuitBreaker
from app.retrieval.manager.observability import TelemetryManager
from app.retrieval.manager.retrieval_manager import RetrievalManager

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

# Validation, Normalization & Metrics services singletons
_validation_service = ValidationService()
_context_service = ContextService()
_query_processor = QueryProcessor()
_metrics_service = MetricsService()

# Repositories singletons
_retrieval_repo = RetrievalRepository()
_metadata_repo = MetadataRepository()

# Manager helpers singletons
_manager_validator = RetrievalValidator(_validation_service)
_session_builder = RetrievalSessionBuilder()
_execution_manager = RetrievalExecutionManager()
_result_builder = RetrievalResultBuilder()
_circuit_breaker = ProviderCircuitBreaker(failure_threshold=3, recovery_timeout_seconds=10.0)
_telemetry_manager = TelemetryManager()


def get_retrieval_service() -> RetrievalService:
    """Dependency Injection provider tree constructing and resolving the RetrievalService hierarchy."""
    # Resolve providers list from registry
    mock_p = provider_registry.get_provider("mock")
    qdrant_p = provider_registry.get_provider("qdrant")
    postgres_p = provider_registry.get_provider("postgres")
    
    # Instantiate concurrent pipelines for target strategy scopes
    semantic_pipeline = RetrievalPipeline([qdrant_p, mock_p], _circuit_breaker)
    keyword_pipeline = RetrievalPipeline([postgres_p, mock_p], _circuit_breaker)
    hybrid_pipeline = RetrievalPipeline([qdrant_p, postgres_p, mock_p], _circuit_breaker)
    
    # Instantiate search strategies
    semantic_strategy = SemanticRetrievalStrategy(semantic_pipeline)
    keyword_strategy = KeywordRetrievalStrategy(keyword_pipeline)
    hybrid_strategy = HybridRetrievalStrategy(hybrid_pipeline)
    
    strategies = [semantic_strategy, keyword_strategy, hybrid_strategy]
    
    # Instantiate orchestrator and coordinator
    orchestrator = RetrievalOrchestrator(strategies)
    coordinator = RetrievalCoordinator(orchestrator)
    
    # Instantiate Retrieval Manager
    manager = RetrievalManager(
        validator=_manager_validator,
        session_builder=_session_builder,
        coordinator=coordinator,
        execution_manager=_execution_manager,
        result_builder=_result_builder,
        telemetry_manager=_telemetry_manager,
        query_processor=_query_processor,
        cache_manager=_cache_manager,
        retrieval_repository=_retrieval_repo,
        metadata_repository=_metadata_repo
    )
    
    # Return high-level coordinate service
    from app.retrieval.context.context_factory import RetrievalContextFactory
    factory = RetrievalContextFactory(_query_processor)
    return RetrievalService(manager, factory)
