import logging
import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from app.core.logging import request_id_ctx

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request-response correlation, timing, and structured logging.

    Generates a unique request ID, injects it into context logging, calculates
    execution latency, and attaches header responses.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Check if the client already passed a Request ID, otherwise generate one
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Set the request ID in context variables so all logs within this task share it
        token = request_id_ctx.set(request_id)

        start_time = time.time()

        # Log details about incoming request
        logger.info(
            f"Request Started: {request.method} {request.url.path} "
            f"from client {request.client.host if request.client else 'unknown'}"
        )

        try:
            response = await call_next(request)

            # Compute execution latency
            duration = time.time() - start_time
            duration_str = f"{duration * 1000:.2f}ms"

            # Log details about completed response
            logger.info(
                f"Request Finished: {request.method} {request.url.path} "
                f"- Status: {response.status_code} - Latency: {duration_str}"
            )

            # Inject the custom headers back into response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = duration_str

            return response

        except Exception as exc:
            duration = time.time() - start_time
            duration_str = f"{duration * 1000:.2f}ms"
            logger.error(
                f"Request Failed: {request.method} {request.url.path} "
                f"- Exception: {str(exc)} - Latency: {duration_str}"
            )
            raise exc
        finally:
            # Ensure token reset to prevent context leakage across requests
            request_id_ctx.reset(token)
