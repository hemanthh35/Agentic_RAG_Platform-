from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.retrieval.schemas.query import RetrievalResultItem


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
        query: str,
        limit: int,
        threshold: float,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResultItem]:
        """Orchestrate chunk retrieval operations and format priority context lists."""
        pass
