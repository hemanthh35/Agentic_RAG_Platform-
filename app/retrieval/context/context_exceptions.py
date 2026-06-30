from typing import Any, Optional
from fastapi import status
from app.core.exceptions import AppException


class ContextException(AppException):
    """Base exception for all retrieval context failures."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None
    ):
        super().__init__(message, status_code=status_code, details=details)


class ContextCreationError(ContextException):
    """Exception raised when retrieval context construction fails."""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class ContextValidationError(ContextException):
    """Exception raised when retrieval context structural validation fails."""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )
