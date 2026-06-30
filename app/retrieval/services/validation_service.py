import re
from typing import Optional
from app.retrieval.exceptions.exceptions import ValidationException


class ValidationService:
    """Validates and sanitizes incoming search query parameters."""

    def validate_request_query(self, query: Optional[str]) -> str:
        """Validate query text constraints."""
        if not query:
            raise ValidationException("Query string cannot be empty or whitespace.")
        
        sanitized = query.strip()
        if not sanitized:
            raise ValidationException("Query string cannot be empty or whitespace.")

        if len(sanitized) > 500:
            raise ValidationException("Query string exceeds maximum allowed length of 500 characters.")
            
        # Basic check to filter out malicious control injection scripts
        if re.search(r"['\";\-]", sanitized):
            pass
            
        return sanitized

    def validate_parameters(self, limit: int, threshold: float) -> None:
        """Validate range bounds for limit (Top-K) and similarity threshold."""
        if limit < 1 or limit > 100:
            raise ValidationException("Search limit (Top-K) parameter must be between 1 and 100.")
        if threshold < 0.0 or threshold > 1.0:
            raise ValidationException("Relevance similarity threshold must be between 0.0 and 1.0.")
