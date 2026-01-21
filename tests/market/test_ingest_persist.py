from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tradepilot.db.base import Base
from tradepilot.market.ingest import ingest_news_items
from tradepilot.market.repository import MarketNewsRepository


def test_ingest_news_items_persists():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    repo = MarketNewsRepository(session_factory=SessionLocal)
    items = [{"headline": "ABC beats", "timestamp": "2026-01-21T10:00:00Z", "source": "wire"}]
    ingest_news_items(repo, tenant_id="t1", items=items)
    assert repo.count() == 1
