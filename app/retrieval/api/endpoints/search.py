from fastapi import APIRouter, Depends, HTTPException, status

from app.retrieval.schemas.query import RetrievalRequest, RetrievalResponse
from app.retrieval.services.retrieval_service import RetrievalService
from app.retrieval.dependencies.dependencies import get_retrieval_service
from app.retrieval.exceptions.exceptions import ValidationException

router = APIRouter()


@router.post(
    "/search",
    response_model=RetrievalResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute context retrieval for search queries"
)
async def retrieve_knowledge_context(
    request: RetrievalRequest,
    service: RetrievalService = Depends(get_retrieval_service)
):
    """
    Unified knowledge retrieval endpoint. 
    Routes requests through selected search strategies (semantic, keyword, hybrid) 
    and outputs validated context chunks.
    """
    try:
        return await service.retrieve_context(request)
    except ValidationException as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err.message)
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retrieval engine failed to execute query search: {str(err)}"
        )
