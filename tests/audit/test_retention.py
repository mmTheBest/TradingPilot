from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tradepilot.audit.retention import prune_positions_deltas
from tradepilot.db.base import Base
from tradepilot.db.models.positions import PositionsDelta


def test_prune_positions_deltas_removes_old_rows():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    cutoff = (datetime.now(tz=timezone.utc) - timedelta(days=365)).isoformat()

    with SessionLocal() as session:
        session.add(
            PositionsDelta(
                id="d1",
                tenant_id="t1",
                book_id="b1",
                event_ts="2020-01-01T00:00:00Z",
                reason="sync",
                ops_json=[],
                payload_hash="x",
                op_count=0,
            )
        )
        session.commit()

    deleted = prune_positions_deltas(SessionLocal, cutoff_ts=cutoff)
    assert deleted == 1
