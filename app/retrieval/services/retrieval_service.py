import logging

from app.retrieval.interfaces.service_interface import BaseRetrievalService
from app.retrieval.manager.retrieval_manager import RetrievalManager
from app.retrieval.schemas.query import RetrievalRequest, RetrievalResponse

logger = logging.getLogger(__name__)


class RetrievalService(BaseRetrievalService):
    """High-level coordinate service delegating retrieval workflow pipelines to the RetrievalManager."""

    def __init__(self, manager: RetrievalManager):
        self.manager = manager

    @property
    def orchestrator(self):
        """Retrieve registered strategies orchestrator instance."""
        return self.manager.coordinator._orchestrator

    async def retrieve_context(self, request: RetrievalRequest) -> RetrievalResponse:
        """Delegate search context queries to the RetrievalManager coordinator."""
        logger.info(f"RetrievalService routing query search request for: '{request.query}'")
        return await self.manager.execute_retrieval(request)
