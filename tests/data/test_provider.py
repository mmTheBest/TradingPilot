from tradepilot.data.provider import DataSnapshot, InMemoryDataProvider


def test_in_memory_provider_returns_snapshot():
    snapshot = DataSnapshot(
        positions_age_minutes=1,
        limits_age_minutes=2,
        current_exposure=100.0,
        absolute_limit=200.0,
        relative_limit_pct=0.2,
        book_notional=1000.0,
        adv=500.0,
        positions_as_of_ts="2026-01-19T09:30:00Z",
        limits_version_id="limits-1",
        issuer_id="issuer-1",
        sector_id="sector-1",
        issuer_exposure=100.0,
        issuer_absolute_limit=1000.0,
        issuer_relative_limit_pct=0.2,
        sector_exposure=100.0,
        sector_absolute_limit=2000.0,
        sector_relative_limit_pct=0.3,
        symbol_price=100.0,
        symbol_notional=1000.0,
        fx_rate_snapshot_id="fx-1",
    )
    provider = InMemoryDataProvider(snapshot=snapshot)

    returned = provider.get_snapshot(tenant_id="tenant-1", book_id="book-1", symbol="AAPL")

    assert returned == snapshot


def test_snapshot_has_symbol_price_fields():
    snapshot = DataSnapshot(
        positions_age_minutes=1,
        limits_age_minutes=1,
        current_exposure=0.0,
        absolute_limit=100.0,
        relative_limit_pct=0.1,
        book_notional=1000.0,
        adv=0.0,
        positions_as_of_ts="2026-01-21T09:30:00Z",
        limits_version_id="v1",
        issuer_id="issuer-1",
        sector_id="sector-1",
        issuer_exposure=0.0,
        issuer_absolute_limit=100.0,
        issuer_relative_limit_pct=0.1,
        sector_exposure=0.0,
        sector_absolute_limit=100.0,
        sector_relative_limit_pct=0.1,
        symbol_price=100.0,
        symbol_notional=1000.0,
    )
    assert snapshot.symbol_price == 100.0
