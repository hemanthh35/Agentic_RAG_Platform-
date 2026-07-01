import logging

from app.retrieval.interfaces.service_interface import BaseRetrievalService
from app.retrieval.manager.retrieval_manager import RetrievalManager
from app.retrieval.schemas.query import RetrievalRequest, RetrievalResponse
from app.retrieval.context.context_factory import RetrievalContextFactory

logger = logging.getLogger(__name__)


class RetrievalService(BaseRetrievalService):
    """High-level coordinate service delegating retrieval workflow pipelines to the RetrievalManager."""

    def __init__(self, manager: RetrievalManager, factory: RetrievalContextFactory):
        self.manager = manager
        self.factory = factory

    @property
    def orchestrator(self):
        """Retrieve registered strategies orchestrator instance."""
        return self.manager.coordinator._orchestrator

    async def retrieve_context(self, request: RetrievalRequest) -> RetrievalResponse:
        """Delegate search context queries to the RetrievalManager coordinator."""
        # Create Retrieval Context from incoming request
        context = self.factory.create_from_request(request)
        
        logger.info(
            f"[CorrelationID: {context.tracing.correlation_id}] RetrievalService routing query "
            f"search request: '{context.query.original_query}'"
        )
        
        return await self.manager.execute_retrieval(context)

