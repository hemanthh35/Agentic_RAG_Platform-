from app.services.health import HealthService


def get_health_service() -> HealthService:
    """Dependency injection provider for HealthService.

    Returns:
        An instance of HealthService.
    """
    return HealthService()
