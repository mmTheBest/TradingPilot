from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tradepilot.db.base import Base
from tradepilot.db.models.fx import FxRateSnapshot
from tradepilot.ingest.repository import IngestRepository


def test_fx_ingest_writes_snapshot():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    repo = IngestRepository(session_factory=SessionLocal)
    repo.record_fx_ingest(
        tenant_id="t1",
        book_id="b1",
        as_of_ts="2026-01-20T10:00:00Z",
        reason="positions_sync",
        rates=[{"vendor": "bg", "base_ccy": "USD", "quote_ccy": "EUR", "mid_rate": 1.1}],
        snapshot_id="snap-1",
    )

    with SessionLocal() as session:
        row = session.query(FxRateSnapshot).first()
        assert row.snapshot_id == "snap-1"
