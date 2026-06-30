import logging
from typing import List, Dict, Optional, Any

from app.retrieval.interfaces.strategy_interface import BaseRetrievalStrategy
from app.retrieval.schemas.query import RetrievalResultItem
from app.retrieval.config.settings import retrieval_settings

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
        query: str,
        limit: int,
        threshold: float,
        strategy_name: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResultItem]:
        """Resolves the strategy and executes it."""
        strategy = self._strategies.get(strategy_name.lower())
        if not strategy:
            fallback = retrieval_settings.DEFAULT_RETRIEVAL_STRATEGY
            logger.warning(
                f"Search strategy '{strategy_name}' not found. "
                f"Falling back to default: {fallback}"
            )
            strategy = self._strategies.get(fallback.lower())
            if not strategy:
                raise ValueError(
                    f"Invalid search strategy '{strategy_name}'. "
                    f"No registered fallback found for '{fallback}'."
                )

        return await strategy.execute(
            query=query,
            limit=limit,
            threshold=threshold,
            filters=filters
        )

    @property
    def registered_strategies(self) -> List[str]:
        """Returns a list of all registered search strategy names."""
        return list(self._strategies.keys())
