from tradepilot.market.impact import compute_impact


def test_compute_impact_sums_exposure():
    positions = [{"symbol": "A", "notional": 100}, {"symbol": "B", "notional": 50}]
    assert compute_impact(positions) == 150
