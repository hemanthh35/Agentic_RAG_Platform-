import uuid
from sqlalchemy import Column, DateTime, String, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class Document(Base):
    """SQLAlchemy model representing the documents metadata table.

    Serves as the foundation for parsed, partitioned, or indexed files.
    """

    __tablename__ = "documents"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
    )
    original_filename = Column(String, nullable=False)
    stored_filename = Column(String, nullable=False)
    bucket_name = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_status = Column(String, default="pending", nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
