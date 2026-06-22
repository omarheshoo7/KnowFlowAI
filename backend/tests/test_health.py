from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_returns_200():
    response = client.get("/api/health")
    assert response.status_code == 200


def test_health_status_ok():
    response = client.get("/api/health")
    data = response.json()
    assert data["status"] == "ok"


def test_health_response_shape():
    response = client.get("/api/health")
    data = response.json()
    assert "service" in data
    assert "version" in data
