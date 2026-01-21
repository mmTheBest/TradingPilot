from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tradepilot.db.base import Base
from tradepilot.db.models.positions import PositionsDelta, PositionsSnapshotFull
from tradepilot.ingest.repository import IngestRepository


def test_positions_ingest_writes_snapshot_and_delta():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    repo = IngestRepository(session_factory=SessionLocal)
    as_of_ts = "2026-01-20T10:00:00Z"
    rows = [{"symbol": "AAPL", "quantity": 10, "price": 100.0, "currency": "USD"}]

    repo.record_positions_ingest(
        tenant_id="t1",
        book_id="b1",
        as_of_ts=as_of_ts,
        reason="scheduled",
        rows=rows,
    )

    with SessionLocal() as session:
        assert session.query(PositionsSnapshotFull).count() == 1
        assert session.query(PositionsDelta).count() == 1
