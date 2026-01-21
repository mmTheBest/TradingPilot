from fastapi.testclient import TestClient

from tradepilot.main import app


def test_query_book_endpoint_exists():
    client = TestClient(app)
    response = client.get("/api/v1/query/book", params={"book_id": "b1"})
    assert response.status_code == 200
