from abc import ABC, abstractmethod
from app.retrieval.schemas.query import RetrievalRequest, RetrievalResponse


class BaseRetrievalService(ABC):
    """Abstract interface defining the entry point for retrieval service logic."""

    @abstractmethod
    async def retrieve_context(self, request: RetrievalRequest) -> RetrievalResponse:
        """Entry coordinate handler for checking, retrieving, and logging context requests."""
        pass
