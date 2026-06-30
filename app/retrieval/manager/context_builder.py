from typing import List
from app.retrieval.schemas.query import RetrievalResultItem
from app.retrieval.services.context_service import ContextService


class RetrievalContextBuilder:
    """Helper building formatted context strings for LLM injection."""

    def __init__(self, context_service: ContextService):
        self._context_service = context_service

    def build_llm_context(self, results: List[RetrievalResultItem]) -> str:
        """Concatenate result chunks into formatted text blocks."""
        return self._context_service.format_context_block(results)
