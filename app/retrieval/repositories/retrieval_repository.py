import logging
from typing import Optional
from app.retrieval.context.retrieval_context import RetrievalContext

logger = logging.getLogger(__name__)


class RetrievalRepository:
    """Repository handling search query logging and RAG analytics tracking."""

    def log_search(
        self,
        query: str,
        strategy: str,
        result_count: int,
        latency_ms: float,
        context: Optional[RetrievalContext] = None
    ) -> None:
        """Log search metrics to analytics layer."""
        correlation_id = context.tracing.correlation_id if context else "None"
        logger.info(
            f"[CorrelationID: {correlation_id}] [Search Analytics] Query: '{query}' | Strategy: '{strategy}' | "
            f"Results: {result_count} | Latency: {latency_ms:.2f}ms"
        )

