from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status

from app.dependencies.services import get_document_service
from app.schemas.document import DocumentResponse, PaginatedDocumentResponse
from app.services.document import DocumentService

router = APIRouter()


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new document",
)
async def upload_document(
    file: UploadFile = File(..., description="The document file to upload"),
    title: Optional[str] = Form(None, description="Optional title, defaults to filename"),
    description: Optional[str] = Form(None, description="Optional description"),
    document_service: DocumentService = Depends(get_document_service),
):
    """
    Upload a document. The file is saved in Supabase storage and metadata in the database.
    Supported types: PDF, DOCX, TXT, Markdown.
    Max size: 10MB.
    """
    return await document_service.upload_document(title, description, file)


@router.get(
    "",
    response_model=PaginatedDocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="List documents",
)
def list_documents(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Records to return"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc or desc)"),
    search: Optional[str] = Query(None, description="Search in title or description"),
    status: Optional[str] = Query(None, description="Filter by status"),
    document_service: DocumentService = Depends(get_document_service),
):
    """
    Retrieve a paginated list of documents with optional filtering and sorting.
    """
    return document_service.list_documents(skip, limit, sort_by, sort_order, search, status)


@router.get(
    "/{id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get document metadata",
)
def get_document(
    id: UUID,
    document_service: DocumentService = Depends(get_document_service),
):
    """
    Retrieve metadata for a single document.
    """
    return document_service.get_document(id)


@router.get(
    "/{id}/download",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get document download URL",
)
async def get_download_url(
    id: UUID,
    document_service: DocumentService = Depends(get_document_service),
):
    """
    Retrieve a signed URL to download the document from Supabase.
    """
    url = await document_service.get_download_url(id)
    return {"download_url": url}


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document",
)
async def delete_document(
    id: UUID,
    document_service: DocumentService = Depends(get_document_service),
):
    """
    Delete a document completely (removes storage file and database record).
    """
    await document_service.delete_document(id)
