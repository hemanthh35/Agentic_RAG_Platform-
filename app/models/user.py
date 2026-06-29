import uuid
from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base


class User(Base):
    """SQLAlchemy model representing the users table.

    Used as the foundation for user account credentials.
    """

    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
    )
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
