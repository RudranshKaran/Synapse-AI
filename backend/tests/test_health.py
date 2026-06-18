"""Tests for the health check endpoint."""

from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Health endpoint test suite."""

    def test_health_returns_healthy(self, client: TestClient) -> None:
        """GET /api/v1/health should return {'status': 'healthy'}."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_health_has_correct_content_type(self, client: TestClient) -> None:
        """Health response should be application/json."""
        response = client.get("/api/v1/health")
        assert response.headers["content-type"] == "application/json"
