from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tradepilot.db.base import Base
from tradepilot.db.models.ingest import IngestRun
from tradepilot.ingest.adapters.fixtures import FixtureFxAdapter, FixturePositionsAdapter
from tradepilot.ingest.queue import IngestQueue
from tradepilot.ingest.repository import IngestRepository
from tradepilot.ingest.worker import IngestWorker


def test_worker_processes_positions_job():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    queue = IngestQueue(session_factory=SessionLocal)
    repo = IngestRepository(session_factory=SessionLocal)
    positions_adapter = FixturePositionsAdapter(
        as_of_ts="2026-01-20T10:00:00Z",
        rows=[{"symbol": "AAPL", "quantity": 10, "price": 100.0, "currency": "USD"}],
    )
    fx_adapter = FixtureFxAdapter(
        rows=[{"vendor": "bg", "base_ccy": "USD", "quote_ccy": "USD", "mid_rate": 1.0}]
    )

    queue.enqueue("t1", "b1", "positions", reason="scheduled")
    worker = IngestWorker(
        session_factory=SessionLocal,
        queue=queue,
        repository=repo,
        positions_adapter=positions_adapter,
        fx_adapter=fx_adapter,
    )

    processed = worker.run_once("positions")
    assert processed == 1

    with SessionLocal() as session:
        assert session.query(IngestRun).count() == 1
