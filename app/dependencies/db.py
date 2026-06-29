from typing import Generator
from sqlalchemy.orm import Session
from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Dependency provider that yields a database session and ensures it is closed after request lifecycle.

    Yields:
        An active SQLAlchemy Session instance or None.
    """
    db = None
    if SessionLocal is not None:
        db = SessionLocal()
    try:
        yield db
    finally:
        if db is not None:
            db.close()
