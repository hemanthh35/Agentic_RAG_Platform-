from pydantic import BaseModel, Field


class ServiceStatus(BaseModel):
    """Schema representing connectivity statuses of external resource dependencies."""

    database: str = Field(
        ...,
        description="Database connection state ('connected' or 'disconnected')",
    )
    supabase: str = Field(
        ...,
        description="Supabase connection state ('connected' or 'disconnected')",
    )


class HealthStatusData(BaseModel):
    """Schema for root health information payload."""

    status: str = Field(
        ..., description="Overall health state ('healthy' or 'degraded')"
    )
    version: str = Field(..., description="Version of the running application")
    environment: str = Field(..., description="Current environment deployment")
    uptime_seconds: float = Field(
        ..., description="Server module runtime duration in seconds"
    )
    timestamp: str = Field(
        ..., description="ISO 8601 formatted UTC timestamp of health query evaluation"
    )
    response_time_ms: float = Field(
        ..., description="Execution processing time in milliseconds"
    )
    services: ServiceStatus = Field(
        ..., description="Breakdown of specific internal integrations"
    )


class HealthResponse(BaseModel):
    """Standardized envelope schema for successful health checks."""

    success: bool = Field(
        True, description="Indicates whether the health lookup was successful"
    )
    data: HealthStatusData = Field(
        ..., description="The structured health report payload"
    )
