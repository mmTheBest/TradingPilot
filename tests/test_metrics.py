from fastapi.testclient import TestClient

from tradepilot.main import app


def test_metrics_endpoint_exists():
    client = TestClient(app)
    response = client.get("/metrics", headers={"x-api-key": "test"})
    assert response.status_code in (401, 200)


def test_metrics_requires_auth():
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 401
