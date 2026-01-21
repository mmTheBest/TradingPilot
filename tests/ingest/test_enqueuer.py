from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tradepilot.db.base import Base
from tradepilot.db.models.book import Book
from tradepilot.db.models.ingest import IngestRun
from tradepilot.ingest.enqueuer import IngestEnqueuer
from tradepilot.ingest.queue import IngestQueue


def test_enqueuer_adds_jobs_when_stale():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        session.add(
            Book(
                id="b1",
                tenant_id="t1",
                portfolio_id=None,
                desk_id=None,
                base_currency="USD",
            )
        )
        session.commit()

    queue = IngestQueue(session_factory=SessionLocal)
    enqueuer = IngestEnqueuer(session_factory=SessionLocal, queue=queue)

    enqueued = enqueuer.enqueue_due(now_ts="2026-01-20T10:10:00Z")

    assert enqueued == 3
    assert queue.pending_count("t1", "b1", "positions") == 1
    assert queue.pending_count("t1", "b1", "limits") == 1
    assert queue.pending_count("t1", "b1", "reference") == 1


def test_enqueuer_skips_when_recent():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        session.add(
            Book(
                id="b1",
                tenant_id="t1",
                portfolio_id=None,
                desk_id=None,
                base_currency="USD",
            )
        )
        session.add(
            IngestRun(
                id="run-1",
                tenant_id="t1",
                book_id="b1",
                data_type="positions",
                started_at="2026-01-20T10:00:00Z",
                finished_at="2026-01-20T10:01:00Z",
                status="succeeded",
                as_of_ts=None,
                payload_hash=None,
                row_count=1,
                error=None,
            )
        )
        session.add(
            IngestRun(
                id="run-2",
                tenant_id="t1",
                book_id="b1",
                data_type="limits",
                started_at="2026-01-20T10:00:00Z",
                finished_at="2026-01-20T10:02:00Z",
                status="succeeded",
                as_of_ts=None,
                payload_hash=None,
                row_count=1,
                error=None,
            )
        )
        session.add(
            IngestRun(
                id="run-3",
                tenant_id="t1",
                book_id="b1",
                data_type="reference",
                started_at="2026-01-20T10:00:00Z",
                finished_at="2026-01-20T10:02:00Z",
                status="succeeded",
                as_of_ts=None,
                payload_hash=None,
                row_count=1,
                error=None,
            )
        )
        session.commit()

    queue = IngestQueue(session_factory=SessionLocal)
    enqueuer = IngestEnqueuer(session_factory=SessionLocal, queue=queue)

    enqueued = enqueuer.enqueue_due(now_ts="2026-01-20T10:03:00Z")

    assert enqueued == 0
    assert queue.pending_count("t1", "b1", "positions") == 0
    assert queue.pending_count("t1", "b1", "limits") == 0
    assert queue.pending_count("t1", "b1", "reference") == 0
