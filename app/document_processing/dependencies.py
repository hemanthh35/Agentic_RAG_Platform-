from fastapi import Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.dependencies.services import get_storage_service
from app.services.storage import StorageService
from app.repositories.document import DocumentRepository
from app.document_processing.services.queue import FastAPIBackgroundQueue
from app.document_processing.services.processing_service import DocumentProcessingService


def get_document_processing_service(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    storage: StorageService = Depends(get_storage_service)
) -> DocumentProcessingService:
    """Dependency injection provider for DocumentProcessingService with enqueued BackgroundTasks."""
    repository = DocumentRepository(db)
    queue = FastAPIBackgroundQueue(background_tasks)
    return DocumentProcessingService(repository, storage, queue)
