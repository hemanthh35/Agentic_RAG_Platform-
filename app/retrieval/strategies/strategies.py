import logging
from typing import List, Optional, Dict, Any

from app.retrieval.interfaces.base import BaseRetrievalStrategy, BaseRetrievalProvider
from app.retrieval.schemas.query import RetrievalResultItem

logger = logging.getLogger(__name__)


class SemanticRetrievalStrategy(BaseRetrievalStrategy):
    """Retrieval strategy prioritizing semantic/vector search indices."""

    def __init__(self, providers: List[BaseRetrievalProvider]):
        self.providers = providers

    @property
    def name(self) -> str:
        return "semantic"

    async def execute(
        self,
        query: str,
        limit: int,
        threshold: float,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResultItem]:
        logger.info(f"Executing semantic retrieval strategy for query '{query}' (threshold={threshold})")
        # In a real deployment, we query Qdrant. For testing/fallback, we inspect mock as well.
        for provider in self.providers:
            if provider.name in ("qdrant", "mock"):
                results = await provider.retrieve(query, limit, filters)
                # Keep if mock returns data, filter by score
                filtered = [r for r in results if r.score >= threshold]
                if filtered:
                    return filtered
        return []


class KeywordRetrievalStrategy(BaseRetrievalStrategy):
    """Retrieval strategy prioritizing traditional keyword FTS search indices."""

    def __init__(self, providers: List[BaseRetrievalProvider]):
        self.providers = providers

    @property
    def name(self) -> str:
        return "keyword"

    async def execute(
        self,
        query: str,
        limit: int,
        threshold: float,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResultItem]:
        logger.info(f"Executing keyword retrieval strategy for query '{query}' (threshold={threshold})")
        # In a real deployment, we query PostgreSQL FTS.
        for provider in self.providers:
            if provider.name in ("postgres", "mock"):
                results = await provider.retrieve(query, limit, filters)
                filtered = [r for r in results if r.score >= threshold]
                if filtered:
                    return filtered
        return []


class HybridRetrievalStrategy(BaseRetrievalStrategy):
    """Retrieval strategy combining semantic vector and keyword results, sorting by score."""

    def __init__(self, providers: List[BaseRetrievalProvider]):
        self.providers = providers

    @property
    def name(self) -> str:
        return "hybrid"

    async def execute(
        self,
        query: str,
        limit: int,
        threshold: float,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResultItem]:
        logger.info(f"Executing hybrid retrieval strategy for query '{query}' (threshold={threshold})")
        all_results = []
        for provider in self.providers:
            # Query Qdrant, Postgres, and fallback Mock
            if provider.name in ("qdrant", "postgres", "mock"):
                res = await provider.retrieve(query, limit, filters)
                all_results.extend(res)

        # Deduplicate chunks and filter by threshold score
        seen_ids = set()
        dedup_results = []
        for r in all_results:
            if r.chunk_id not in seen_ids:
                seen_ids.add(r.chunk_id)
                if r.score >= threshold:
                    dedup_results.append(r)

        # Sort combined results descending by score
        dedup_results.sort(key=lambda x: x.score, reverse=True)
        return dedup_results[:limit]
