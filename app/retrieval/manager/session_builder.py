from uuid import uuid4
from typing import Dict, Any, Union
from app.retrieval.schemas.query import RetrievalRequest
from app.retrieval.context.retrieval_context import RetrievalContext


class RetrievalSessionBuilder:
    """Builder initializing unique session parameters and authorization indexes."""

    def build_session(self, request_or_context: Union[RetrievalRequest, RetrievalContext]) -> Dict[str, Any]:
        """Formulate a unique execution context dictionary for logging and security verification."""
        if isinstance(request_or_context, RetrievalContext):
            session_id = request_or_context.execution.session_id or request_or_context.request.request_id
            user_id = request_or_context.user.user_id
            search_type = request_or_context.query.query_type or "default"
            collection = request_or_context.metadata.collection_name or "documents"
            active_strategy = request_or_context.strategy.strategy_name
        else:
            session_id = request_or_context.session_id if request_or_context.session_id else str(uuid4())
            user_id = str(request_or_context.user_id) if request_or_context.user_id else "anonymous"
            search_type = request_or_context.search_type or "default"
            collection = request_or_context.collection or "documents"
            active_strategy = request_or_context.strategy
        
        return {
            "session_id": session_id,
            "user_id": user_id,
            "search_type": search_type,
            "collection": collection,
            "active_strategy": active_strategy
        }

