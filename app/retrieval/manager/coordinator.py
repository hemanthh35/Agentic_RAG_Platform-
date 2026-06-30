from typing import List, Optional, Dict, Any
from app.retrieval.orchestrator.retrieval_orchestrator import RetrievalOrchestrator
from app.retrieval.schemas.query import RetrievalResultItem


class RetrievalCoordinator:
    """Routing coordinator coordinating pipeline calls to the orchestrator."""

    def __init__(self, orchestrator: RetrievalOrchestrator):
        self._orchestrator = orchestrator

    async def retrieve(
        self,
        query: str,
        limit: int,
        threshold: float,
        strategy: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResultItem]:
        """Trigger strategy execution pipelines under the target orchestrator."""
        return await self._orchestrator.execute_retrieval(
            query=query,
            limit=limit,
            threshold=threshold,
            strategy_name=strategy,
            filters=filters
        )
