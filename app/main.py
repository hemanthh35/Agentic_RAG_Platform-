import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.middleware.logging import RequestLoggingMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.core.logging import setup_logging

# Setup application logging
setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events manager for startup and shutdown execution hooks.

    Initializes connection systems and cleans them up when shutting down.
    """
    logger.info("Initializing system startup hooks...")
    # Startup placeholder points for Redis, Qdrant/Milvus, Elasticsearch, Langfuse
    logger.info("System startup hooks execution completed.")

    yield

    logger.info("Initializing system shutdown hooks...")
    # Shutdown hooks for closing database connection pools, third-party clients
    logger.info("System shutdown hooks execution completed.")


app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# Register custom and global exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Register CORS Middleware
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Register custom correlation/tracking Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# Include main versioned routing hierarchy
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
def read_root():
    """Default greeting redirect endpoint."""
    return {
        "message": f"Welcome to {settings.API_TITLE}. Go to {settings.API_V1_STR}/docs for details."
    }
