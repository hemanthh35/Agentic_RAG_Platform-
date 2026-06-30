import uuid
from sqlalchemy import Column, DateTime, String, Integer, Float, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base


class ExtractedText(Base):
    """SQLAlchemy model representing the clean extracted text for a document."""

    __tablename__ = "extracted_texts"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
    )
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    text_content = Column(Text, nullable=False)
    extraction_timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    parser_used = Column(String, nullable=False)
    version_number = Column(Integer, default=1, nullable=False)
    character_count = Column(Integer, nullable=False)
    word_count = Column(Integer, nullable=False)
    page_count = Column(Integer, nullable=False)
    line_count = Column(Integer, nullable=False)
    extraction_status = Column(String, nullable=False)
    processing_duration = Column(Float, nullable=False)

    document = relationship("Document", back_populates="extracted_text")
