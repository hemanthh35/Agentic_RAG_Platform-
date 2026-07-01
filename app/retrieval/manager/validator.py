from typing import Union
from app.retrieval.schemas.query import RetrievalRequest
from app.retrieval.context.retrieval_context import RetrievalContext
from app.retrieval.services.validation_service import ValidationService


class RetrievalValidator:
    """Validation coordinator checking search request constraints."""

    def __init__(self, validation_service: ValidationService):
        self._validation_service = validation_service

    def validate(self, request_or_context: Union[RetrievalRequest, RetrievalContext]) -> None:
        """Validate input query and range parameter bounds. Raises ValidationException on violation."""
        if isinstance(request_or_context, RetrievalContext):
            query = request_or_context.query.original_query
            limit = request_or_context.configuration.top_k
            threshold = request_or_context.configuration.similarity_threshold
        else:
            query = request_or_context.query
            limit = request_or_context.limit if request_or_context.limit else 10
            threshold = request_or_context.threshold if request_or_context.threshold is not None else 0.0

        self._validation_service.validate_request_query(query)
        self._validation_service.validate_parameters(limit, threshold)

