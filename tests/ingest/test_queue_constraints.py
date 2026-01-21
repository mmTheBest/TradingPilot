import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from tradepilot.db.base import Base
from tradepilot.db.models.ingest import IngestRefreshQueue


def test_ingest_queue_dedupe_unique():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        session.add(
            IngestRefreshQueue(
                id="job-1",
                tenant_id="t1",
                book_id="b1",
                data_type="positions",
                status="pending",
                attempts=0,
                next_attempt_at="2026-01-20T10:00:00Z",
                last_error=None,
                dedupe_key="t1:b1:positions",
                reason="scheduled",
                created_at="2026-01-20T10:00:00Z",
                updated_at="2026-01-20T10:00:00Z",
            )
        )
        session.add(
            IngestRefreshQueue(
                id="job-2",
                tenant_id="t1",
                book_id="b1",
                data_type="positions",
                status="pending",
                attempts=0,
                next_attempt_at="2026-01-20T10:01:00Z",
                last_error=None,
                dedupe_key="t1:b1:positions",
                reason="scheduled",
                created_at="2026-01-20T10:01:00Z",
                updated_at="2026-01-20T10:01:00Z",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()
