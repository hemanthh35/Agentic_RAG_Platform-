from app.services.health import HealthService
from app.services.storage import StorageService
from app.services.document import DocumentService
from app.repositories.document import DocumentRepository
from app.dependencies.db import get_db
from fastapi import Depends
from sqlalchemy.orm import Session


def get_health_service() -> HealthService:
    """Dependency injection provider for HealthService.

    Returns:
        An instance of HealthService.
    """
    return HealthService()


def get_storage_service() -> StorageService:
    """Dependency injection provider for StorageService."""
    return StorageService()


def get_document_service(
    db: Session = Depends(get_db),
    storage: StorageService = Depends(get_storage_service)
) -> DocumentService:
    """Dependency injection provider for DocumentService."""
    repository = DocumentRepository(db)
    return DocumentService(repository, storage)
