import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class RetrievalExecutionManager:
    """State manager supervising execution progress and pipeline status transitions."""

    def __init__(self):
        self._states: Dict[str, Any] = {}

    def update_state(self, session_id: str, state: str) -> None:
        """Log state changes and update running transition status mapping."""
        self._states[session_id] = state
        logger.info(f"[Retrieval Session: {session_id}] Execution State updated: {state}")

    def get_state(self, session_id: str) -> str:
        """Resolve current state for an active session ID."""
        return self._states.get(session_id, "unknown")
