import logging
import uuid
from typing import List, Optional, Dict, Any

from app.retrieval.interfaces.base import BaseRetrievalProvider
from app.retrieval.schemas.query import RetrievalResultItem

logger = logging.getLogger(__name__)


class MockRetrievalProvider(BaseRetrievalProvider):
    """Fallback active placeholder provider returning mock context chunks for integration testing."""

    @property
    def name(self) -> str:
        return "mock"

    async def retrieve(
        self,
        query: str,
        limit: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResultItem]:
        doc_id = str(uuid.uuid4())
        logger.info(f"Mock retrieval provider triggered for query '{query}' (limit={limit})")
        return [
            RetrievalResultItem(
                chunk_id=str(uuid.uuid4()),
                document_id=doc_id,
                chunk_index=0,
                text_content=f"This is a mock text chunk context containing '{query}' matching details in section Introduction.",
                character_count=110,
                word_count=14,
                page_number=1,
                section_title="Introduction",
                score=0.95,
                original_filename="manual_agent.pdf"
            ),
            RetrievalResultItem(
                chunk_id=str(uuid.uuid4()),
                document_id=doc_id,
                chunk_index=1,
                text_content=f"Here is another relevant mock segment explaining system setup queries matching '{query}' in section Configurations.",
                character_count=130,
                word_count=18,
                page_number=3,
                section_title="Configurations",
                score=0.82,
                original_filename="manual_agent.pdf"
            )
        ][:limit]


class QdrantRetrievalProvider(BaseRetrievalProvider):
    """Vector database retrieval connector (Qdrant semantic search wrapper)."""

    @property
    def name(self) -> str:
        return "qdrant"

    async def retrieve(
        self,
        query: str,
        limit: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResultItem]:
        logger.info("Qdrant semantic retrieval connector is not implemented yet in Section 1 (Architecture).")
        return []


class PostgresRetrievalProvider(BaseRetrievalProvider):
    """Relational full-text search retrieval connector (Postgres keyword search wrapper)."""

    @property
    def name(self) -> str:
        return "postgres"

    async def retrieve(
        self,
        query: str,
        limit: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResultItem]:
        logger.info("Postgres full-text keyword retrieval connector is not implemented yet in Section 1 (Architecture).")
        return []
