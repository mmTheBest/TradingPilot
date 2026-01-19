from tradepilot.replay.assembler import apply_deltas


def test_apply_deltas_orders_by_time():
    base = {"AAPL": 10}
    deltas = [
        {"symbol": "AAPL", "delta": -2, "event_ts": "2026-01-19T10:01:00Z"},
        {"symbol": "AAPL", "delta": 5, "event_ts": "2026-01-19T10:02:00Z"},
    ]
    result = apply_deltas(base, deltas)
    assert result["AAPL"] == 13
