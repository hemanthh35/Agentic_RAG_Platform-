import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Session-scoped fixture to provide a test client for FastAPI.

    Using 'with' statement triggers startup and shutdown lifespan events.
    """
    with TestClient(app) as test_client:
        yield test_client
