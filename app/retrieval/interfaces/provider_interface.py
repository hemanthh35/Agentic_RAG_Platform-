from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.retrieval.schemas.query import RetrievalResultItem
from app.retrieval.context.retrieval_context import RetrievalContext


class BaseRetrievalProvider(ABC):
    """Abstract interface defining required behaviors for data retrieval connectors."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique provider identifier key."""
        pass

    @abstractmethod
    async def retrieve(
        self,
        context: RetrievalContext
    ) -> List[RetrievalResultItem]:
        """Fetch chunks matching search criteria from external data storage systems."""
        pass

