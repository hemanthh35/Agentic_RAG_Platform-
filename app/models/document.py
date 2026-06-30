import uuid
from sqlalchemy import Column, DateTime, String, Integer, Float, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
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
    
    # Document Processing Pipeline Fields
    processing_status = Column(String, default="Uploaded", nullable=False)
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    processing_completed_at = Column(DateTime(timezone=True), nullable=True)
    processing_duration = Column(Float, nullable=True)
    processing_error = Column(String, nullable=True)
    parser_used = Column(String, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    page_count = Column(Integer, nullable=True)
    character_count = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    line_count = Column(Integer, nullable=True)
    extracted_text_version = Column(Integer, default=1, nullable=False)
    extraction_completed = Column(Boolean, default=False, nullable=False)

    extracted_text = relationship(
        "ExtractedText", uselist=False, back_populates="document", cascade="all, delete-orphan"
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
