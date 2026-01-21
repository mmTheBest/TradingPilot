from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tradepilot.auth.repository import ApiKeyRepository
from tradepilot.db.base import Base


def test_api_key_repository_roundtrip():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    repo = ApiKeyRepository(session_factory=SessionLocal)
    key_id = repo.create_key(tenant_id="t1", role="OPS", owner="service-a")
    record = repo.get_key(key_id)
    assert record.tenant_id == "t1"
    assert record.owner == "service-a"
