import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tradepilot.data.provider import DataSnapshot, InMemoryDataProvider
from tradepilot.integrations.emsx import FakeEmsxClient
from tradepilot.trades.models import TradeRequest
from tradepilot.trades.override_repository import OverrideRepository
from tradepilot.trades.repository import TradeRepository
from tradepilot.trades.service import RiskCheckFailed, TradeService
from tradepilot.db.base import Base


def test_override_allows_when_stale():
    snapshot = DataSnapshot(
        positions_age_minutes=10,
        limits_age_minutes=1,
        current_exposure=1000.0,
        absolute_limit=2000.0,
        relative_limit_pct=1.0,
        book_notional=5000.0,
        adv=0.0,
        positions_as_of_ts="2026-01-21T09:30:00Z",
        limits_version_id="v1",
        issuer_id="issuer-1",
        sector_id="sector-1",
        issuer_exposure=1000.0,
        issuer_absolute_limit=2000.0,
        issuer_relative_limit_pct=1.0,
        sector_exposure=1000.0,
        sector_absolute_limit=2000.0,
        sector_relative_limit_pct=1.0,
        symbol_price=100.0,
        symbol_notional=1000.0,
    )
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    service = TradeService(
        emsx_client=FakeEmsxClient(),
        data_provider=InMemoryDataProvider(snapshot=snapshot),
        repository=TradeRepository(session_factory=SessionLocal),
        override_repository=OverrideRepository(session_factory=SessionLocal),
    )
    request = TradeRequest(
        tenant_id="t1",
        book_id="b1",
        symbol="AAPL",
        side="sell",
        quantity=1,
        price=100.0,
        override_requested=True,
        override_reason="stale positions",
    )
    staged = service.stage_trade(request, actor_role="OPS")
    assert staged.status == "staged"


def test_override_rejected_without_role():
    snapshot = DataSnapshot(
        positions_age_minutes=10,
        limits_age_minutes=1,
        current_exposure=1000.0,
        absolute_limit=2000.0,
        relative_limit_pct=1.0,
        book_notional=5000.0,
        adv=0.0,
        positions_as_of_ts="2026-01-21T09:30:00Z",
        limits_version_id="v1",
        issuer_id="issuer-1",
        sector_id="sector-1",
        issuer_exposure=1000.0,
        issuer_absolute_limit=2000.0,
        issuer_relative_limit_pct=1.0,
        sector_exposure=1000.0,
        sector_absolute_limit=2000.0,
        sector_relative_limit_pct=1.0,
        symbol_price=100.0,
        symbol_notional=1000.0,
    )
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    service = TradeService(
        emsx_client=FakeEmsxClient(),
        data_provider=InMemoryDataProvider(snapshot=snapshot),
        repository=TradeRepository(session_factory=SessionLocal),
        override_repository=OverrideRepository(session_factory=SessionLocal),
    )
    request = TradeRequest(
        tenant_id="t1",
        book_id="b1",
        symbol="AAPL",
        side="sell",
        quantity=1,
        price=100.0,
        override_requested=True,
        override_reason="stale positions",
    )
    with pytest.raises(RiskCheckFailed):
        service.stage_trade(request, actor_role=None)
