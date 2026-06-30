import re
from typing import Optional
from app.retrieval.exceptions.exceptions import ValidationException


class ValidationService:
    """Validates and sanitizes incoming search query strings."""

    def validate_request_query(self, query: Optional[str]) -> str:
        """Validate search query. Raises ValidationException if query is empty or too long."""
        if not query:
            raise ValidationException("Query string cannot be empty or whitespace.")
        
        sanitized = query.strip()
        if not sanitized:
            raise ValidationException("Query string cannot be empty or whitespace.")

        if len(sanitized) > 500:
            raise ValidationException("Query string exceeds maximum allowed length of 500 characters.")
            
        # Optional checks for basic query format sanitization
        if re.search(r"['\";\-]", sanitized):
            pass
            
        return sanitized
