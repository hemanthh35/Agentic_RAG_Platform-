from typing import Optional, Tuple, List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc

from app.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    """Repository for managing Document model database operations."""

    def __init__(self, db: Session):
        super().__init__(Document, db)

    def get_paginated_and_filtered(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        search: Optional[str] = None,
        status: Optional[str] = None
    ) -> Tuple[List[Document], int]:
        """Retrieve paginated and filtered documents.
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            sort_by: Column to sort by
            sort_order: 'asc' or 'desc'
            search: Search string for title or description
            status: Filter by status
            
        Returns:
            Tuple containing the list of documents and the total count matching the filters.
        """
        query = self.db.query(self.model)

        # Apply filters
        if status:
            query = query.filter(self.model.upload_status == status)
            
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    self.model.original_filename.ilike(search_term),
                    self.model.description.ilike(search_term)
                )
            )

        # Total count before pagination
        total = query.count()

        # Sorting
        sort_column = getattr(self.model, sort_by, self.model.created_at)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Pagination
        documents = query.offset(skip).limit(limit).all()

        return documents, total
