import logging
from typing import List, Dict, Optional, Any

from app.retrieval.interfaces.strategy_interface import BaseRetrievalStrategy
from app.retrieval.schemas.query import RetrievalResultItem
from app.retrieval.config.settings import retrieval_settings
from app.retrieval.context.retrieval_context import RetrievalContext

logger = logging.getLogger(__name__)


class RetrievalOrchestrator:
    """Orchestrates query execution by routing requests to registered strategies."""

    def __init__(self, strategies: List[BaseRetrievalStrategy]):
        self._strategies: Dict[str, BaseRetrievalStrategy] = {
            s.name.lower(): s for s in strategies
        }
        logger.info(f"RetrievalOrchestrator initialized with strategies: {list(self._strategies.keys())}")

    def register_strategy(self, strategy: BaseRetrievalStrategy) -> None:
        """Register a new strategy dynamically."""
        self._strategies[strategy.name.lower()] = strategy
        logger.info(f"Registered new retrieval strategy: {strategy.name}")

    async def execute_retrieval(
        self,
        context: RetrievalContext
    ) -> List[RetrievalResultItem]:
        """Resolves the strategy and executes it."""
        strategy_name = context.strategy.strategy_name
        strategy = self._strategies.get(strategy_name.lower())
        correlation_id = context.tracing.correlation_id
        
        if not strategy:
            fallback = retrieval_settings.DEFAULT_RETRIEVAL_STRATEGY
            logger.warning(
                f"[CorrelationID: {correlation_id}] Search strategy '{strategy_name}' not found. "
                f"Falling back to default: {fallback}"
            )
            strategy = self._strategies.get(fallback.lower())
            if not strategy:
                raise ValueError(
                    f"Invalid search strategy '{strategy_name}'. "
                    f"No registered fallback found for '{fallback}'."
                )

        logger.info(
            f"[CorrelationID: {correlation_id}] Orchestrator executing strategy: '{strategy.name}'"
        )
        return await strategy.execute(context)

    @property
    def registered_strategies(self) -> List[str]:
        """Returns a list of all registered search strategy names."""
        return list(self._strategies.keys())

