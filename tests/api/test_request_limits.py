from fastapi.testclient import TestClient

from tradepilot.main import app


def test_request_size_limit():
    client = TestClient(app)
    payload = {"data": "x" * 2_000_000}
    response = client.post("/api/v1/trades/stage", json=payload)
    assert response.status_code in (413, 422)
