import logging
from typing import Any, Optional
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base application exception for all custom errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class DatabaseException(AppException):
    """Exception raised for database operations failures."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class NotFoundException(AppException):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message, status_code=status.HTTP_404_NOT_FOUND, details=details
        )


class BadRequestException(AppException):
    """Exception raised for bad or invalid request parameters."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message, status_code=status.HTTP_400_BAD_REQUEST, details=details
        )


async def app_exception_handler(
    request: Request, exc: AppException
) -> JSONResponse:
    """JSON response handler for all custom AppException errors."""
    logger.error(
        f"AppException: {exc.message} - Status: {exc.status_code} - Details: {exc.details}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details,
            },
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """JSON response handler for FastAPI/Pydantic request validation errors."""
    logger.error(f"Validation error: {exc.errors()}")
    # Convert error locations to a friendlier format if desired
    formatted_errors = []
    for error in exc.errors():
        formatted_errors.append(
            {
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "ValidationError",
                "message": "Request validation failed",
                "details": formatted_errors,
            },
        },
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """JSON response handler for Starlette HTTPExceptions."""
    logger.error(
        f"HTTPException: Status {exc.status_code} - Details: {exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": "HTTPException",
                "message": str(exc.detail),
                "details": None,
            },
        },
    )


async def global_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """JSON response handler for any unhandled unexpected errors."""
    logger.exception("An unhandled exception occurred")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "InternalServerError",
                "message": "An unexpected error occurred. Please contact system support.",
                "details": None,
            },
        },
    )
