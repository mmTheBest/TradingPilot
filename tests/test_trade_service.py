import pytest

from tradepilot.data.provider import DataSnapshot, InMemoryDataProvider
from tradepilot.integrations.emsx import FakeEmsxClient
from tradepilot.trades.models import TradeRequest
from tradepilot.trades.service import RiskCheckFailed, TradeService


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
        fx_rate_snapshot_id="fx-1",
    )
    service = TradeService(
        emsx_client=FakeEmsxClient(),
        data_provider=InMemoryDataProvider(snapshot=snapshot),
    )
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
        fx_rate_snapshot_id="fx-1",
    )
    service = TradeService(
        emsx_client=FakeEmsxClient(),
        data_provider=InMemoryDataProvider(snapshot=snapshot),
        positions_sla_minutes=5,
    )
    request = TradeRequest(tenant_id="tenant-1", book_id="book-1", symbol="AAPL", side="buy", quantity=10)
    with pytest.raises(RiskCheckFailed):
        service.stage_trade(request)
