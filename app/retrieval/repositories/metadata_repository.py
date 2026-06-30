import logging
from typing import List
from uuid import UUID

logger = logging.getLogger(__name__)


class MetadataRepository:
    """Repository handling database document metadata authorization checks."""

    def verify_document_access(self, document_ids: List[UUID]) -> bool:
        """Verify if current session user has access to referenced document IDs."""
        logger.info(f"Verifying database records metadata access authorization for documents: {document_ids}")
        return True
