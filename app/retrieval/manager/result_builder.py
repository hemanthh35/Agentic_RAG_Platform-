from typing import List, Dict, Any, Optional
from app.retrieval.schemas.query import RetrievalResponse, RetrievalResultItem
from app.retrieval.context.retrieval_context import RetrievalContext


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
        timeline: Optional[Dict[str, float]] = None,
        context: Optional[RetrievalContext] = None
    ) -> RetrievalResponse:
        """Compose context records, confidence scores, and latency metrics into response DTO."""
        provider_stats = {
            p: {"latency_ms": round(latency_ms / len(providers) if providers else latency_ms, 2)}
            for p in providers
        }
        
        response_meta = metadata or {}
        if context:
            # Enrich response metadata with tracing context information
            response_meta = {
                **response_meta,
                "correlation_id": context.tracing.correlation_id,
                "trace_id": context.tracing.trace_id,
                "span_id": context.tracing.span_id,
            }
            if context.tracing.parent_span_id:
                response_meta["parent_span_id"] = context.tracing.parent_span_id

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

