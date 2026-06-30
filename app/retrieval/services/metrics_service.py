import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class MetricsService:
    """Observability service collecting search queries latency and caching metrics."""

    def __init__(self):
        self._metrics: Dict[str, Any] = {
            "total_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "failed_queries": 0,
            "total_latency_ms": 0.0
        }

    def record_query(self, latency_ms: float, cache_hit: bool = False, success: bool = True) -> None:
        """Increment count parameters and aggregate latency metrics."""
        self._metrics["total_queries"] += 1
        self._metrics["total_latency_ms"] += latency_ms
        if cache_hit:
            self._metrics["cache_hits"] += 1
        else:
            self._metrics["cache_misses"] += 1
        
        if not success:
            self._metrics["failed_queries"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Aggregate stats and return query averages."""
        avg_latency = 0.0
        if self._metrics["total_queries"] > 0:
            avg_latency = self._metrics["total_latency_ms"] / self._metrics["total_queries"]
            
        hit_ratio = 0.0
        total_cache_attempts = self._metrics["cache_hits"] + self._metrics["cache_misses"]
        if total_cache_attempts > 0:
            hit_ratio = self._metrics["cache_hits"] / total_cache_attempts

        return {
            **self._metrics,
            "average_latency_ms": round(avg_latency, 2),
            "cache_hit_ratio": round(hit_ratio, 2)
        }
