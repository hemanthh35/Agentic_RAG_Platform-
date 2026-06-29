from unittest.mock import patch
from fastapi.testclient import TestClient


def test_health_endpoint_degraded(client: TestClient) -> None:
    """Test the health check endpoint under a degraded scenario.

    Mocks database and Supabase checks to return False, ensuring status is
    degraded.
    """
    with patch(
        "app.services.health.check_db_connection", return_value=False
    ), patch(
        "app.services.health.check_supabase_connection", return_value=False
    ):
        response = client.get("/api/v1/health")
        assert response.status_code == 200

        payload = response.json()
        assert payload["success"] is True
        assert "data" in payload

        data = payload["data"]
        assert data["status"] == "degraded"
        assert data["services"]["database"] == "disconnected"
        assert data["services"]["supabase"] == "disconnected"
        assert isinstance(data["uptime_seconds"], float)
        assert "version" in data
        assert "environment" in data


def test_health_endpoint_healthy(client: TestClient) -> None:
    """Test the health check endpoint under a fully healthy scenario.

    Mocks database and Supabase checks to return True.
    """
    with patch(
        "app.services.health.check_db_connection", return_value=True
    ), patch(
        "app.services.health.check_supabase_connection", return_value=True
    ):
        response = client.get("/api/v1/health")
        assert response.status_code == 200

        payload = response.json()
        assert payload["success"] is True

        data = payload["data"]
        assert data["status"] == "healthy"
        assert data["services"]["database"] == "connected"
        assert data["services"]["supabase"] == "connected"
