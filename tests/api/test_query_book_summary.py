from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from tradepilot.db.base import Base
from tradepilot.db.models.positions import PositionsSnapshotFull
from tradepilot.main import app
from tradepilot.api import query as query_api


def test_query_book_returns_summary():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        session.add(
            PositionsSnapshotFull(
                id="p1",
                tenant_id="t1",
                book_id="b1",
                as_of_ts="2026-01-21T10:00:00Z",
                net_exposure=100.0,
                gross_notional=200.0,
                snapshot_json=[{"symbol": "AAPL", "quantity": 10, "price": 10.0}],
                payload_hash="h1",
            )
        )
        session.commit()

    query_api.SessionLocal = SessionLocal
    client = TestClient(app)
    response = client.get("/api/v1/query/book", params={"book_id": "b1", "tenant_id": "t1"})
    assert response.status_code == 200
    data = response.json()
    assert data["gross_notional"] == 200.0
