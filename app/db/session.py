import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

logger = logging.getLogger(__name__)

# Base class for declarative database models
Base = declarative_base()

# Configure SQLAlchemy engine and SessionLocal session factory
try:
    # Use pool_pre_ping to check connection viability before checkout
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    logger.info("SQLAlchemy database engine configured successfully.")
except Exception as e:
    logger.error(
        f"Failed to initialize SQLAlchemy database engine with URL {settings.DATABASE_URL}: {e}"
    )
    engine = None
    SessionLocal = None


def check_db_connection() -> bool:
    """Verify if the database is online and reachable.

    Returns:
        True if connection is successful, False otherwise.
    """
    if engine is None:
        logger.warning(
            "Database engine is not initialized. Connection check failed."
        )
        return False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.warning(f"Database connection check failed: {e}")
        return False
