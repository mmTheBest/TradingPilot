from uuid import UUID

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tradepilot.data.provider import DataSnapshot, InMemoryDataProvider
from tradepilot.db.base import Base
from tradepilot.integrations.emsx import FakeEmsxClient
from tradepilot.trades.models import TradeRequest
from tradepilot.trades.repository import TradeRepository
from tradepilot.trades.service import RiskCheckFailed, TradeService


def build_service(snapshot: DataSnapshot) -> TradeService:
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    repo = TradeRepository(session_factory=SessionLocal)
    return TradeService(
        emsx_client=FakeEmsxClient(),
        data_provider=InMemoryDataProvider(snapshot=snapshot),
        repository=repo,
    )


def test_trade_request_accepts_price():
    request = TradeRequest(
        tenant_id="tenant-1",
        book_id="book-1",
        symbol="AAPL",
        side="buy",
        quantity=10,
        price=100.0,
    )
    assert request.price == 100.0


def test_trade_service_blocks_on_failed_risk_check():
    snapshot = DataSnapshot(
        positions_age_minutes=1,
        limits_age_minutes=1,
        current_exposure=900,
        absolute_limit=1000,
        relative_limit_pct=1.0,
        book_notional=100_000,
        adv=10_000,
        positions_as_of_ts="2026-01-19T09:30:00Z",
        limits_version_id="limits-1",
        issuer_id="issuer-1",
        sector_id="sector-1",
        issuer_exposure=900,
        issuer_absolute_limit=10_000,
        issuer_relative_limit_pct=1.0,
        sector_exposure=900,
        sector_absolute_limit=10_000,
        sector_relative_limit_pct=1.0,
        fx_rate_snapshot_id="fx-1",
    )
    service = build_service(snapshot)
    request = TradeRequest(tenant_id="tenant-1", book_id="book-1", symbol="AAPL", side="buy", quantity=200)
    with pytest.raises(RiskCheckFailed):
        service.stage_trade(request)


def test_trade_service_blocks_on_stale_positions():
    snapshot = DataSnapshot(
        positions_age_minutes=10,
        limits_age_minutes=1,
        current_exposure=0,
        absolute_limit=1000,
        relative_limit_pct=1.0,
        book_notional=100_000,
        adv=10_000,
        positions_as_of_ts="2026-01-19T09:30:00Z",
        limits_version_id="limits-1",
        issuer_id="issuer-1",
        sector_id="sector-1",
        issuer_exposure=0,
        issuer_absolute_limit=10_000,
        issuer_relative_limit_pct=1.0,
        sector_exposure=0,
        sector_absolute_limit=10_000,
        sector_relative_limit_pct=1.0,
        fx_rate_snapshot_id="fx-1",
    )
    service = build_service(snapshot)
    service.positions_sla_minutes = 5
    request = TradeRequest(tenant_id="tenant-1", book_id="book-1", symbol="AAPL", side="buy", quantity=10)
    with pytest.raises(RiskCheckFailed):
        service.stage_trade(request)


def test_stage_trade_returns_internal_trade_id():
    snapshot = DataSnapshot(
        positions_age_minutes=1,
        limits_age_minutes=1,
        current_exposure=0,
        absolute_limit=1000,
        relative_limit_pct=1.0,
        book_notional=100_000,
        adv=10_000,
        positions_as_of_ts="2026-01-19T09:30:00Z",
        limits_version_id="limits-1",
        issuer_id="issuer-1",
        sector_id="sector-1",
        issuer_exposure=0,
        issuer_absolute_limit=10_000,
        issuer_relative_limit_pct=1.0,
        sector_exposure=0,
        sector_absolute_limit=10_000,
        sector_relative_limit_pct=1.0,
        fx_rate_snapshot_id="fx-1",
    )
    service = build_service(snapshot)
    request = TradeRequest(tenant_id="tenant-1", book_id="book-1", symbol="AAPL", side="buy", quantity=10)
    staged = service.stage_trade(request)

    UUID(staged.trade_id)
    assert staged.emsx_order_id is not None
    assert staged.trade_id != staged.emsx_order_id


def test_stale_gate_enqueues_refresh():
    class DummyQueue:
        def __init__(self):
            self.calls: list[str] = []

        def enqueue(self, tenant_id, book_id, data_type, reason):
            self.calls.append(data_type)
            return "job-1"

    class DummyRepo:
        def create_staged_trade(self, **kwargs):
            raise AssertionError("should not be called")

    snapshot = DataSnapshot(
        positions_age_minutes=10,
        limits_age_minutes=10,
        current_exposure=0.0,
        absolute_limit=100.0,
        relative_limit_pct=0.1,
        book_notional=1000.0,
        adv=0.0,
        positions_as_of_ts="2026-01-20T09:00:00Z",
        limits_version_id="v1",
        issuer_id="issuer-1",
        sector_id="sector-1",
        issuer_exposure=0.0,
        issuer_absolute_limit=1000.0,
        issuer_relative_limit_pct=1.0,
        sector_exposure=0.0,
        sector_absolute_limit=1000.0,
        sector_relative_limit_pct=1.0,
        fx_rate_snapshot_id=None,
    )
    provider = InMemoryDataProvider(snapshot=snapshot)
    queue = DummyQueue()
    service = TradeService(
        emsx_client=FakeEmsxClient(),
        data_provider=provider,
        repository=DummyRepo(),
        ingest_queue=queue,
    )
    request = TradeRequest(
        tenant_id="t1",
        book_id="b1",
        symbol="AAPL",
        side="buy",
        quantity=10,
        order_type="market",
        limit_price=None,
    )

    with pytest.raises(RiskCheckFailed):
        service.stage_trade(request)

    assert "positions" in queue.calls
    assert "limits" in queue.calls
