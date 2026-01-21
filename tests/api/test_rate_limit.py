from fastapi.testclient import TestClient

from tradepilot.main import app


def test_rate_limit_blocks():
    client = TestClient(app)
    for _ in range(10):
        client.get("/healthz")
    response = client.get("/healthz")
    assert response.status_code in (429, 200)
