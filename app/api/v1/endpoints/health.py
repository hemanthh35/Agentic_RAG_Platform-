from fastapi import APIRouter, Depends
from app.dependencies.services import get_health_service
from app.schemas.health import HealthResponse
from app.services.health import HealthService
from app.utils.formatters import format_response

router = APIRouter()


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health Check API",
    description=(
        "Performs self-checks on system parameters, database connection, "
        "and Supabase connectivity status."
    ),
)
def get_health(
    health_service: HealthService = Depends(get_health_service),
) -> HealthResponse:
    """Endpoint function to query system operational health status."""
    health_status = health_service.get_health_status()
    return format_response(success=True, data=health_status)
