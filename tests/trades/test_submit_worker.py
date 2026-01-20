from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from tradepilot.db.base import Base
from tradepilot.db.models.tradeflow import StagedTradeRecord, TradeSubmitQueue
from tradepilot.trades.submit_worker import RetryPolicy, SubmitWorker


class FailingEmsxClient:
    def submit_order(self, _order_id: str) -> str:
        raise RuntimeError("emsx down")


def test_submit_worker_retries_with_backoff():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    now = datetime.now(tz=timezone.utc)
    with SessionLocal() as session:
        session.add(
            StagedTradeRecord(
                trade_id="trade-1",
                tenant_id="tenant-1",
                book_id="book-1",
                symbol="AAPL",
                side="buy",
                quantity=10,
                order_type="market",
                limit_price=None,
                status="approved",
                emsx_order_id="emsx-1",
                positions_as_of_ts=now.isoformat(),
                limits_version_id="limits-1",
                fx_rate_snapshot_id=None,
                created_at=now.isoformat(),
            )
        )
        session.add(
            TradeSubmitQueue(
                id="job-1",
                trade_id="trade-1",
                status="pending",
                attempts=0,
                next_attempt_at=now.isoformat(),
                last_error=None,
                created_at=now.isoformat(),
                updated_at=now.isoformat(),
            )
        )
        session.commit()

    worker = SubmitWorker(
        session_factory=SessionLocal,
        emsx_client=FailingEmsxClient(),
        retry_policy=RetryPolicy(),
    )
    processed = worker.run_once()
    assert processed == 1

    with SessionLocal() as session:
        job = session.get(TradeSubmitQueue, "job-1")
        assert job.attempts == 1
        assert job.status == "pending"
        assert job.next_attempt_at > now.isoformat()
