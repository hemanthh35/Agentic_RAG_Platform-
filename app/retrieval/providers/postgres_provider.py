import logging
from typing import List, Optional, Dict, Any

from app.retrieval.interfaces.provider_interface import BaseRetrievalProvider
from app.retrieval.schemas.query import RetrievalResultItem
from app.retrieval.context.retrieval_context import RetrievalContext

logger = logging.getLogger(__name__)


class PostgresRetrievalProvider(BaseRetrievalProvider):
    """Relational full-text search retrieval connector (Postgres keyword search wrapper placeholder)."""

    @property
    def name(self) -> str:
        return "postgres"

    async def retrieve(
        self,
        context: RetrievalContext
    ) -> List[RetrievalResultItem]:
        correlation_id = context.tracing.correlation_id
        logger.info(
            f"[CorrelationID: {correlation_id}] Postgres full-text keyword retrieval connector is not implemented yet in Section 2.1."
        )
        return []

