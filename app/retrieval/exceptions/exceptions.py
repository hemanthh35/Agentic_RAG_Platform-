from typing import Any, Optional
from fastapi import status
from app.core.exceptions import AppException


class RetrievalException(AppException):
    """Base exception for all search and retrieval failures."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None
    ):
        super().__init__(message, status_code=status_code, details=details)


class ValidationException(RetrievalException):
    """Exception raised for invalid user queries or malformed filters."""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class ProviderException(RetrievalException):
    """Exception raised when an external indexing/retrieval database fails (e.g. Qdrant timeout)."""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details
        )


class StrategyException(RetrievalException):
    """Exception raised when the orchestrator fails to execute or route a retrieval query."""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class CacheException(RetrievalException):
    """Exception raised when cache operations fail."""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )
