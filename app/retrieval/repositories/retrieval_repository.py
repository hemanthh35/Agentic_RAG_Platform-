import logging

logger = logging.getLogger(__name__)


class RetrievalRepository:
    """Repository handling search query logging and RAG analytics tracking."""

    def log_search(self, query: str, strategy: str, result_count: int, latency_ms: float) -> None:
        """Log search metrics to analytics layer."""
        logger.info(
            f"[Search Analytics] Query: '{query}' | Strategy: '{strategy}' | "
            f"Results: {result_count} | Latency: {latency_ms:.2f}ms"
        )
