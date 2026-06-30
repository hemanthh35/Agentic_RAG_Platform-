from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.retrieval.schemas.query import RetrievalResultItem


class BaseRetrievalProvider(ABC):
    """Abstract Base Class defining contracts for external retrieval systems (Qdrant, Postgres)."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the provider system."""
        pass

    @abstractmethod
    async def retrieve(
        self,
        query: str,
        limit: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResultItem]:
        """Query the target indexing data source to pull matched items."""
        pass


class BaseRetrievalStrategy(ABC):
    """Abstract Base Class defining orchestration logic for merging different retrieval systems."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the strategy."""
        pass

    @abstractmethod
    async def execute(
        self,
        query: str,
        limit: int,
        threshold: float,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResultItem]:
        """Execute the retrieval pipeline strategy."""
        pass


class QueryPreprocessor(ABC):
    """Abstract Base Class for normalizing, cleaning, and preparing queries before search."""

    @abstractmethod
    def preprocess(self, query: str) -> str:
        """Normalize or expand input query keywords."""
        pass
