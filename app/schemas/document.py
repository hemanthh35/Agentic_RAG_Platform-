from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentBase(BaseModel):
    """Base Document Schema with common attributes."""
    original_filename: str = Field(..., description="The original filename of the document")
    description: Optional[str] = Field(None, description="Optional description of the document")


class DocumentCreate(BaseModel):
    """Schema for document creation."""
    original_filename: str
    stored_filename: str
    bucket_name: str
    storage_path: str
    mime_type: str
    file_size: int
    upload_status: str = "pending"
    description: Optional[str] = None


class DocumentUpdate(BaseModel):
    """Schema for updating document metadata."""
    original_filename: Optional[str] = None
    description: Optional[str] = None
    upload_status: Optional[str] = None


class DocumentResponse(BaseModel):
    """Schema for document responses."""
    id: UUID
    original_filename: str
    stored_filename: str
    bucket_name: str
    storage_path: str
    mime_type: str
    file_size: int
    upload_status: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedDocumentResponse(BaseModel):
    """Schema for paginated document list."""
    items: List[DocumentResponse]
    total: int
    skip: int
    limit: int
