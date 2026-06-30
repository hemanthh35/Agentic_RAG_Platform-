from uuid import uuid4
from typing import Dict, Any
from app.retrieval.schemas.query import RetrievalRequest


class RetrievalSessionBuilder:
    """Builder initializing unique session parameters and authorization indexes."""

    def build_session(self, request: RetrievalRequest) -> Dict[str, Any]:
        """Formulate a unique execution context dictionary for logging and security verification."""
        session_id = request.session_id if request.session_id else str(uuid4())
        user_id = str(request.user_id) if request.user_id else "anonymous"
        
        return {
            "session_id": session_id,
            "user_id": user_id,
            "search_type": request.search_type or "default",
            "collection": request.collection or "documents",
            "active_strategy": request.strategy
        }
