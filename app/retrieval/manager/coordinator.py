from typing import List, Optional, Dict, Any
from app.retrieval.orchestrator.retrieval_orchestrator import RetrievalOrchestrator
from app.retrieval.schemas.query import RetrievalResultItem
from app.retrieval.context.retrieval_context import RetrievalContext


class RetrievalCoordinator:
    """Routing coordinator coordinating pipeline calls to the orchestrator."""

    def __init__(self, orchestrator: RetrievalOrchestrator):
        self._orchestrator = orchestrator

    async def retrieve(
        self,
        context: RetrievalContext
    ) -> List[RetrievalResultItem]:
        """Trigger strategy execution pipelines under the target orchestrator."""
        return await self._orchestrator.execute_retrieval(context)

