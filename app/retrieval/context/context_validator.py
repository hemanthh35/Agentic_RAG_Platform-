from app.retrieval.context.retrieval_context import RetrievalContext
from app.retrieval.context.context_exceptions import ContextValidationError


class RetrievalContextValidator:
    """Enforces validation constraints checking correctness of the context parameters."""

    def validate(self, context: RetrievalContext) -> None:
        """Inspect structure of the context and raise ContextValidationError on violation."""
        if not context.request.request_id:
            raise ContextValidationError("RequestContext request_id is mandatory.")
            
        if not context.query.original_query or not context.query.original_query.strip():
            raise ContextValidationError("Original search query keywords cannot be empty.")
            
        if context.configuration.timeout_sec <= 0.0:
            raise ContextValidationError(
                f"Timeout must be positive. Received: {context.configuration.timeout_sec}"
            )
            
        if not context.provider.selected_providers:
            raise ContextValidationError("Provider list cannot be empty.")
            
        valid_strategies = {"semantic", "keyword", "hybrid"}
        if context.strategy.strategy_name.lower() not in valid_strategies:
            raise ContextValidationError(
                f"Strategy '{context.strategy.strategy_name}' is unrecognized. "
                f"Must be one of: {valid_strategies}"
            )
