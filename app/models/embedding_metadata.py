import uuid
from sqlalchemy import Column, DateTime, String, Integer, Float, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base


class EmbeddingMetadata(Base):
    """SQLAlchemy model representing indexing run configurations for semantic vector chunks."""

    __tablename__ = "embedding_metadata"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
    )
    chunk_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chunks.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    embedding_model = Column(String(100), nullable=False)
    embedding_dimension = Column(Integer, nullable=False)
    generation_time = Column(Float, nullable=True)
    batch_number = Column(Integer, nullable=True)
    index_version = Column(Integer, default=1, nullable=False)
    generation_status = Column(String(50), default="Pending", nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    chunk = relationship("Chunk", back_populates="embedding_metadata")
