from fastapi.testclient import TestClient

from tradepilot.main import app


def test_metrics_endpoint_exists():
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200
