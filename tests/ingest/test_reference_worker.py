from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tradepilot.db.base import Base
from tradepilot.ingest.adapters.base import ReferenceAdapter
from tradepilot.ingest.queue import IngestQueue
from tradepilot.ingest.worker import IngestWorker
from tradepilot.ingest.reference_repository import ReferenceRepository


class DummyReferenceAdapter(ReferenceAdapter):
    def fetch_reference(self):
        return [{"symbol": "AAPL", "issuer_id": "i1", "sector_id": "s1", "taxonomy_id": "t1"}]


def test_reference_worker_persists():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    queue = IngestQueue(session_factory=SessionLocal)
    repo = ReferenceRepository(session_factory=SessionLocal)
    queue.enqueue("t1", "b1", "reference", "schedule")

    worker = IngestWorker(
        session_factory=SessionLocal,
        queue=queue,
        repository=None,
        reference_adapter=DummyReferenceAdapter(),
        reference_repository=repo,
    )
    worker.run_once("reference")
    assert repo.count() == 1
