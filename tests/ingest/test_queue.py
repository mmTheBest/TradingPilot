from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tradepilot.db.base import Base
from tradepilot.ingest.queue import IngestQueue


def test_queue_dedupes_pending_jobs():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    queue = IngestQueue(session_factory=SessionLocal)
    queue.enqueue("t1", "b1", "positions", reason="scheduled")
    queue.enqueue("t1", "b1", "positions", reason="scheduled")

    assert queue.pending_count("t1", "b1", "positions") == 1
