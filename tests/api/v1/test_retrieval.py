import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_retrieval_config():
    """Verify that retrieval/config endpoint returns defaults and registered strategies."""
    response = client.get("/api/v1/retrieval/config")
    assert response.status_code == 200
    data = response.json()
    assert "default_limit" in data
    assert "default_threshold" in data
    assert "default_strategy" in data
    assert "registered_strategies" in data
    assert "semantic" in data["registered_strategies"]
    assert "keyword" in data["registered_strategies"]
    assert "hybrid" in data["registered_strategies"]
    assert data["features"]["semantic_search"] is True


def test_retrieval_search_successful_mock():
    """Verify that retrieval/search returns matching mock chunks for valid queries."""
    payload = {
        "query": "agent configurations",
        "limit": 5,
        "threshold": 0.5,
        "strategy": "hybrid"
    }
    response = client.post("/api/v1/retrieval/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "agent configurations"
    assert len(data["items"]) > 0
    assert data["items"][0]["score"] >= 0.5
    assert "manual_agent.pdf" in data["items"][0]["original_filename"]
    assert "mock" in data["providers_queried"]


def test_retrieval_search_empty_query():
    """Verify that posting empty query returns HTTP 400 Bad Request."""
    payload = {
        "query": "   ",
        "limit": 5,
        "strategy": "semantic"
    }
    response = client.post("/api/v1/retrieval/search", json=payload)
    assert response.status_code == 400
    assert "Query string cannot be empty" in response.json()["error"]["message"]


def test_retrieval_search_long_query():
    """Verify that posting query exceeding 500 characters returns HTTP 400 Bad Request."""
    payload = {
        "query": "a" * 501,
        "limit": 5,
        "strategy": "semantic"
    }
    response = client.post("/api/v1/retrieval/search", json=payload)
    assert response.status_code == 400
    assert "exceeds maximum allowed length" in response.json()["error"]["message"]


def test_retrieval_search_invalid_limit():
    """Verify limit must be between 1 and 100."""
    payload = {
        "query": "valid query",
        "limit": 0,
        "strategy": "semantic"
    }
    # This will fail Pydantic model validation first, raising a 422
    response = client.post("/api/v1/retrieval/search", json=payload)
    assert response.status_code == 422
    
    payload["limit"] = 101
    response = client.post("/api/v1/retrieval/search", json=payload)
    assert response.status_code == 422


def test_retrieval_search_invalid_threshold():
    """Verify relevance similarity threshold score must be between 0.0 and 1.0."""
    payload = {
        "query": "valid query",
        "threshold": -0.1,
        "strategy": "semantic"
    }
    response = client.post("/api/v1/retrieval/search", json=payload)
    assert response.status_code == 422
    
    payload["threshold"] = 1.1
    response = client.post("/api/v1/retrieval/search", json=payload)
    assert response.status_code == 422
