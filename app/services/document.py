import logging
import os
import uuid
from typing import List, Optional

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import AppException
from app.repositories.document import DocumentRepository
from app.schemas.document import DocumentResponse, PaginatedDocumentResponse
from app.services.storage import StorageService

logger = logging.getLogger(__name__)


class DocumentService:
    """Service layer for document workflows and business logic."""

    def __init__(self, repository: DocumentRepository, storage: StorageService):
        self.repository = repository
        self.storage = storage

    async def upload_document(
        self, title: str, description: Optional[str], file: UploadFile
    ) -> DocumentResponse:
        """Handles the complete upload workflow safely."""
        
        # 1. Validation
        if not file.filename:
            raise AppException(status_code=400, detail="Missing filename in upload.")

        # Validate extension
        _, ext = os.path.splitext(file.filename)
        if ext.lower() not in settings.SUPPORTED_DOCUMENT_TYPES:
            raise AppException(
                status_code=400, 
                detail=f"Unsupported file extension: {ext}. Allowed types: {', '.join(settings.SUPPORTED_DOCUMENT_TYPES)}"
            )

        # Validate file size
        file_bytes = await file.read()
        file_size = len(file_bytes)
        
        if file_size == 0:
            raise AppException(status_code=400, detail="Uploaded file is empty.")
            
        if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
            max_mb = settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)
            raise AppException(status_code=413, detail=f"File exceeds maximum size of {max_mb}MB.")

        # 2. Prepare Storage
        internal_id = uuid.uuid4()
        storage_path = str(internal_id)
        content_type = file.content_type or "application/octet-stream"
        
        # 3. Upload to storage
        uploaded_path = None
        try:
            uploaded_path = await self.storage.upload_file(
                file_path=storage_path, 
                file_bytes=file_bytes, 
                content_type=content_type
            )
        except Exception as e:
            # The exception is already logged and raised by StorageService
            raise e

        # 4. Save metadata to DB
        try:
            db_obj = self.repository.create({
                "id": internal_id,
                "original_filename": title or file.filename,
                "stored_filename": storage_path,
                "bucket_name": self.storage.bucket_name,
                "storage_path": storage_path,
                "mime_type": content_type,
                "file_size": file_size,
                "upload_status": "ready",
                "processing_status": "Uploaded",
                "extracted_text_version": 1,
                "extraction_completed": False,
                "description": description
            })
            return DocumentResponse.model_validate(db_obj)
        except Exception as e:
            logger.error(f"Failed to insert document metadata, rolling back storage upload: {e}")
            # Rollback storage
            try:
                if uploaded_path:
                    await self.storage.delete_file(uploaded_path)
            except Exception as rollback_err:
                logger.critical(f"Failed to rollback storage during metadata failure! Orphan file: {uploaded_path}. Error: {rollback_err}")
            
            raise AppException(status_code=500, detail="Database failure. Upload rolled back.")

    def list_documents(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        search: Optional[str] = None,
        status: Optional[str] = None
    ) -> PaginatedDocumentResponse:
        """Retrieves a paginated list of documents."""
        documents, total = self.repository.get_paginated_and_filtered(
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            search=search,
            status=status
        )
        
        items = [DocumentResponse.model_validate(doc) for doc in documents]
        
        return PaginatedDocumentResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )

    def get_document(self, document_id: uuid.UUID) -> DocumentResponse:
        """Retrieves document metadata by ID."""
        doc = self.repository.get(document_id)
        if not doc:
            raise AppException(status_code=404, detail="Document not found.")
        return DocumentResponse.model_validate(doc)

    async def get_download_url(self, document_id: uuid.UUID) -> str:
        """Generates a signed download URL for the document."""
        # 1. Check if document exists
        doc = self.repository.get(document_id)
        if not doc:
            raise AppException(status_code=404, detail="Document not found.")
            
        # 2. Generate signed URL using stored storage path
        return await self.storage.create_signed_url(doc.storage_path)

    async def delete_document(self, document_id: uuid.UUID) -> bool:
        """Deletes a document completely (DB + Storage)."""
        doc = self.repository.get(document_id)
        if not doc:
            raise AppException(status_code=404, detail="Document not found.")
            
        # 1. Delete from storage first using stored storage path
        await self.storage.delete_file(doc.storage_path)
        
        # 2. Delete from DB
        try:
            self.repository.remove(document_id)
            return True
        except Exception as e:
            logger.error(f"Failed to delete metadata after storage file was deleted for {document_id}: {e}")
            raise AppException(status_code=500, detail="Storage deleted but database record failed to delete.")
