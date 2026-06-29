import time
from datetime import datetime, timezone
from typing import Any, Dict
from app.core.config import settings
from app.db.session import check_db_connection
from app.db.supabase import check_supabase_connection

# Capture start time of the service module loading
START_TIME = time.time()


class HealthService:
    """Service responsible for aggregating and assessing application health metadata."""

    def __init__(self) -> None:
        pass

    def get_health_status(self) -> Dict[str, Any]:
        """Assess connectivity of database, supabase and measure uptime.

        Returns:
            A dictionary structure conforming to the health schema response.
        """
        start_perf = time.perf_counter()

        db_ok = check_db_connection()
        supabase_ok = check_supabase_connection()

        # Calculate database and integration querying duration in milliseconds
        response_time_ms = (time.perf_counter() - start_perf) * 1000.0

        uptime_seconds = time.time() - START_TIME
        timestamp_iso = datetime.now(timezone.utc).isoformat()

        # Standard health assessment logic
        status_value = "healthy"
        if not db_ok or not supabase_ok:
            status_value = "degraded"

        return {
            "status": status_value,
            "version": settings.API_VERSION,
            "environment": settings.ENVIRONMENT,
            "uptime_seconds": round(uptime_seconds, 2),
            "timestamp": timestamp_iso,
            "response_time_ms": round(response_time_ms, 2),
            "services": {
                "database": "connected" if db_ok else "disconnected",
                "supabase": "connected" if supabase_ok else "disconnected",
            },
        }
