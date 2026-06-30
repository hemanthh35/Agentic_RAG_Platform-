from typing import List, Dict, Any, Optional
from app.retrieval.schemas.query import RetrievalResponse, RetrievalResultItem


class RetrievalResultBuilder:
    """Formatter constructing search results into unified RetrievalResponse structures."""

    def build_response(
        self,
        query: str,
        results: List[RetrievalResultItem],
        latency_ms: float,
        confidence: float,
        strategy: str,
        providers: List[str],
        metadata: Optional[Dict[str, Any]] = None,
        timeline: Optional[Dict[str, float]] = None
    ) -> RetrievalResponse:
        """Compose context records, confidence scores, and latency metrics into response DTO."""
        provider_stats = {
            p: {"latency_ms": round(latency_ms / len(providers) if providers else latency_ms, 2)}
            for p in providers
        }
        
        response_meta = metadata or {}
        if timeline:
            response_meta = {**response_meta, "execution_timeline_ms": timeline}

        return RetrievalResponse(
            query=query,
            results=results,
            retrieved_chunks=results,
            items=results,
            search_time_ms=round(latency_ms, 2),
            execution_time_ms=round(latency_ms, 2),
            confidence_score=round(confidence, 4),
            search_strategy=strategy,
            strategy_used=strategy,
            metadata=response_meta,
            provider_information=provider_stats,
            total_results=len(results),
            providers_queried=providers
        )
