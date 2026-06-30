import logging
from typing import Dict, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class TelemetryManager:
    """Manages distributed tracing propagation context identifiers and OpenTelemetry callback hooks."""

    def initialize_tracing(
        self,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, str]:
        """Verify and populate Trace, Span and Correlation ID indexes."""
        t_id = trace_id or str(uuid4())
        s_id = span_id or str(uuid4())
        c_id = correlation_id or str(uuid4())
        
        return {
            "trace_id": t_id,
            "span_id": s_id,
            "correlation_id": c_id
        }

    def instrument_provider_start(self, provider_name: str, tracing: Dict[str, str]) -> None:
        """Trigger instrumentation log hooks at beginning of provider calls."""
        logger.info(
            f"[Telemetry Span Start] Provider: '{provider_name}' | "
            f"TraceID: {tracing.get('trace_id')} | SpanID: {tracing.get('span_id')} | "
            f"CorrelationID: {tracing.get('correlation_id')}"
        )

    def instrument_provider_end(self, provider_name: str, tracing: Dict[str, str], duration_ms: float) -> None:
        """Trigger instrumentation log hooks on completion of provider calls."""
        logger.info(
            f"[Telemetry Span End] Provider: '{provider_name}' | Duration: {duration_ms:.2f}ms | "
            f"TraceID: {tracing.get('trace_id')}"
        )
