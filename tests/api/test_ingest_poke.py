from fastapi.testclient import TestClient

from tradepilot.main import app


def test_ingest_poke_requires_auth():
    client = TestClient(app)
    response = client.post(
        "/api/v1/ingest/poke",
        json={"tenant_id": "t1", "book_id": "b1", "data_type": "positions"},
    )
    assert response.status_code == 401
