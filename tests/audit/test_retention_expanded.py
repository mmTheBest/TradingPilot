from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tradepilot.audit.retention import prune_limits_snapshots
from tradepilot.db.base import Base
from tradepilot.db.models.limits import RiskLimitsSnapshotFull


def test_prune_limits_snapshots_removes_old_rows():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    cutoff = (datetime.now(tz=timezone.utc) - timedelta(days=365)).isoformat()

    with SessionLocal() as session:
        session.add(
            RiskLimitsSnapshotFull(
                id="l1",
                tenant_id="t1",
                book_id="b1",
                as_of_ts="2020-01-01T00:00:00Z",
                version_id="v1",
                payload_hash="h1",
            )
        )
        session.commit()

    deleted = prune_limits_snapshots(SessionLocal, cutoff_ts=cutoff)
    assert deleted == 1
