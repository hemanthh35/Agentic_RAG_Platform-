from datetime import datetime, timezone
from typing import Any, Dict, Optional


def format_response(
    success: bool,
    data: Optional[Any] = None,
    error: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Standardizes API JSON response formats across endpoints.

    Args:
        success: True if the request succeeded, False otherwise.
        data: Dictionary, list, or primitive containing the response body.
        error: Dictionary with keys 'code', 'message', and optionally 'details'.

    Returns:
        A structured dictionary representing the standardized response.
    """
    payload: Dict[str, Any] = {"success": success}
    if data is not None:
        payload["data"] = data
    if error is not None:
        payload["error"] = error
    return payload


def get_utc_now() -> datetime:
    """Get the current datetime object localized in UTC.

    Returns:
        A datetime instance representing current UTC time.
    """
    return datetime.now(timezone.utc)


def format_iso_timestamp(dt: datetime) -> str:
    """Format a datetime object into a standard ISO 8601 string.

    Args:
        dt: The datetime instance.

    Returns:
        An ISO formatted datetime string.
    """
    return dt.isoformat()
