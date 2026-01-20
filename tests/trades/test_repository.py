from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tradepilot.db.base import Base
from tradepilot.db.models.tradeflow import StagedTradeRecord, TradeApproval, TradeSubmitQueue
from tradepilot.trades.repository import TradeRepository


def test_repository_creates_trade_and_enqueue():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    repo = TradeRepository(session_factory=SessionLocal)
    now = datetime.now(tz=timezone.utc).isoformat()

    trade_id = repo.create_staged_trade(
        tenant_id="tenant-1",
        book_id="book-1",
        symbol="AAPL",
        side="buy",
        quantity=10,
        order_type="market",
        limit_price=None,
        status="staged",
        emsx_order_id="emsx-1",
        positions_as_of_ts=now,
        limits_version_id="limits-1",
        fx_rate_snapshot_id="fx-1",
    )

    repo.record_approval(
        trade_id=trade_id,
        action="approve",
        reason="ok",
        slack_user_id="U1",
        approver_id="approver-1",
        approver_effective_from=now,
        approver_effective_to=None,
    )
    repo.enqueue_submission(trade_id=trade_id, next_attempt_at=now)

    with SessionLocal() as session:
        assert session.query(StagedTradeRecord).count() == 1
        assert session.query(TradeApproval).count() == 1
        assert session.query(TradeSubmitQueue).count() == 1
