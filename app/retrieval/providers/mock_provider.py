import logging
import uuid
from typing import List, Optional, Dict, Any

from app.retrieval.interfaces.provider_interface import BaseRetrievalProvider
from app.retrieval.schemas.query import RetrievalResultItem
from app.retrieval.context.retrieval_context import RetrievalContext

logger = logging.getLogger(__name__)


class MockRetrievalProvider(BaseRetrievalProvider):
    """Fallback active placeholder provider returning mock context chunks for integration testing."""

    @property
    def name(self) -> str:
        return "mock"

    async def retrieve(
        self,
        context: RetrievalContext
    ) -> List[RetrievalResultItem]:
        query = context.query.original_query
        limit = context.configuration.top_k
        correlation_id = context.tracing.correlation_id
        
        doc_id = str(uuid.uuid4())
        logger.info(
            f"[CorrelationID: {correlation_id}] Mock retrieval provider triggered for query '{query}' (limit={limit})"
        )
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

