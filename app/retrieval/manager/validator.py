from app.retrieval.schemas.query import RetrievalRequest
from app.retrieval.services.validation_service import ValidationService


class RetrievalValidator:
    """Validation coordinator checking search request constraints."""

    def __init__(self, validation_service: ValidationService):
        self._validation_service = validation_service

    def validate(self, request: RetrievalRequest) -> None:
        """Validate input query and range parameter bounds. Raises ValidationException on violation."""
        self._validation_service.validate_request_query(request.query)
        
        limit = request.limit if request.limit else 10
        threshold = request.threshold if request.threshold is not None else 0.0
        self._validation_service.validate_parameters(limit, threshold)
