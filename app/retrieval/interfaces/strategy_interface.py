from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.retrieval.schemas.query import RetrievalResultItem
from app.retrieval.context.retrieval_context import RetrievalContext


class BaseRetrievalStrategy(ABC):
    """Abstract interface defining behaviors for orchestrating and combining retrieval systems."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy lookup name identifier (e.g. semantic, hybrid)."""
        pass

    @abstractmethod
    async def execute(
        self,
        context: RetrievalContext
    ) -> List[RetrievalResultItem]:
        """Orchestrate chunk retrieval operations and format priority context lists."""
        pass

