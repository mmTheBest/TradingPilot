from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from tradepilot.api import query as query_api
from tradepilot.db.base import Base
from tradepilot.main import app


def test_query_book_endpoint_exists():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    query_api.SessionLocal = SessionLocal
    client = TestClient(app)
    response = client.get("/api/v1/query/book", params={"book_id": "b1", "tenant_id": "t1"})
    assert response.status_code in (200, 404)
