from fastapi.testclient import TestClient

from tradepilot.main import app


def test_cors_headers_present():
    client = TestClient(app)
    response = client.options(
        "/healthz",
        headers={"Origin": "http://example.com", "Access-Control-Request-Method": "GET"},
    )
    assert "access-control-allow-origin" in response.headers
