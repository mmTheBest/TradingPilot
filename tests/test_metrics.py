from fastapi.testclient import TestClient

from tradepilot.auth.dependencies import require_api_key
from tradepilot.main import app


def test_metrics_endpoint_exists():
    app.dependency_overrides[require_api_key] = lambda: {"tenant_id": "t1", "role": "OPS"}
    try:
        client = TestClient(app)
        response = client.get("/metrics")
        assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()


def test_metrics_requires_auth():
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 401
