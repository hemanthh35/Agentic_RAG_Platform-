import uuid
from sqlalchemy import Column, DateTime, String, func
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
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="pending", nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
