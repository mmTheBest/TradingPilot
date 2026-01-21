from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tradepilot.db.base import Base
from tradepilot.ingest.reference_repository import ReferenceRepository


def test_reference_repository_upsert():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    repo = ReferenceRepository(session_factory=SessionLocal)
    repo.upsert_securities(
        [{"symbol": "AAPL", "issuer_id": "i1", "sector_id": "s1", "taxonomy_id": "t1"}]
    )
    assert repo.count() == 1
