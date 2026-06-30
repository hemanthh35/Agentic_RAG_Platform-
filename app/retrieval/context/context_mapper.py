from typing import Dict, Any
from app.retrieval.context.retrieval_context import RetrievalContext


class RetrievalContextMapper:
    """Helper mapping RetrievalContext structures to standard serializable dictionaries."""

    def to_dict(self, context: RetrievalContext) -> Dict[str, Any]:
        """Convert read-only pydantic context model to primitive python dictionary structures."""
        return context.model_dump()
