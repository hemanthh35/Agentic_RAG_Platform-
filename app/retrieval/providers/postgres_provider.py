import logging
from typing import List, Optional, Dict, Any

from app.retrieval.interfaces.provider_interface import BaseRetrievalProvider
from app.retrieval.schemas.query import RetrievalResultItem

logger = logging.getLogger(__name__)


class PostgresRetrievalProvider(BaseRetrievalProvider):
    """Relational full-text search retrieval connector (Postgres keyword search wrapper placeholder)."""

    @property
    def name(self) -> str:
        return "postgres"

    async def retrieve(
        self,
        query: str,
        limit: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResultItem]:
        logger.info("Postgres full-text keyword retrieval connector is not implemented yet in Section 2.1.")
        return []
