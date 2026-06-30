import uuid
from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base


class Chunk(Base):
    """SQLAlchemy model representing document text chunks."""

    __tablename__ = "chunks"

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
        nullable=False,
    )
    chunk_index = Column(Integer, nullable=False)
    section_title = Column(String, nullable=True)
    page_number = Column(Integer, nullable=True)
    character_count = Column(Integer, nullable=False)
    word_count = Column(Integer, nullable=False)
    start_position = Column(Integer, nullable=True)
    end_position = Column(Integer, nullable=True)
    chunk_size = Column(Integer, nullable=False)
    chunk_status = Column(String, default="Pending", nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    document = relationship("Document", back_populates="chunks")
    embedding_metadata = relationship(
        "EmbeddingMetadata", uselist=False, back_populates="chunk", cascade="all, delete-orphan"
    )


# Import relationship targets to register them with SQLAlchemy registry
from app.models.embedding_metadata import EmbeddingMetadata  # noqa: F401
