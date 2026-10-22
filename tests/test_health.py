from tests.conftest import client


def test_health_endpoint(client):
    """Test the health endpoint returns healthy status."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"
    assert "models_loaded" in data