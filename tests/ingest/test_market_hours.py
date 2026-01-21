from tradepilot.ingest.scheduler import is_market_hours


def test_market_hours_weekday_open():
    assert is_market_hours("2026-01-21T15:00:00-05:00") is True


def test_market_hours_weekend_closed():
    assert is_market_hours("2026-01-24T15:00:00-05:00") is False
