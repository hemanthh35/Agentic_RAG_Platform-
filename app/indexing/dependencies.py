from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.repositories.document import DocumentRepository
from app.indexing.services.indexing_service import IndexingService


def get_indexing_service(db: Session = Depends(get_db)) -> IndexingService:
    """Dependency injection provider for the semantic IndexingService orchestrator."""
    repository = DocumentRepository(db)
    return IndexingService(repository)
