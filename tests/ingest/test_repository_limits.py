from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tradepilot.db.base import Base
from tradepilot.db.models.limits import RiskLimitsDelta, RiskLimitsSnapshotFull, RiskLimitsVersioned
from tradepilot.ingest.repository import IngestRepository


def test_limits_ingest_writes_version_snapshot_and_delta():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    repo = IngestRepository(session_factory=SessionLocal)

    rows = [
        {
            "dimension": "issuer",
            "dimension_id": "issuer-1",
            "absolute_limit": 100.0,
            "relative_limit_pct": 0.1,
            "effective_from": "2026-01-20T10:00:00Z",
            "effective_to": None,
        }
    ]

    repo.record_limits_ingest(
        tenant_id="t1",
        book_id="b1",
        as_of_ts="2026-01-20T10:00:00Z",
        version_id="v1",
        reason="scheduled",
        rows=rows,
    )

    with SessionLocal() as session:
        assert session.query(RiskLimitsVersioned).count() == 1
        assert session.query(RiskLimitsSnapshotFull).count() == 1
        assert session.query(RiskLimitsDelta).count() == 1

    repo.record_limits_ingest(
        tenant_id="t1",
        book_id="b1",
        as_of_ts="2026-01-20T10:10:00Z",
        version_id="v1",
        reason="scheduled",
        rows=rows,
    )

    with SessionLocal() as session:
        assert session.query(RiskLimitsVersioned).count() == 1
        assert session.query(RiskLimitsSnapshotFull).count() == 2
        assert session.query(RiskLimitsDelta).count() == 1
