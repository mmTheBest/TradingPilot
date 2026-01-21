from tradepilot.risk.exposure import aggregate_exposure_by_issuer


def test_aggregate_exposure_by_issuer():
    positions = [
        {"symbol": "AAA", "notional": 100.0, "issuer_id": "i1"},
        {"symbol": "BBB", "notional": -50.0, "issuer_id": "i1"},
        {"symbol": "CCC", "notional": 25.0, "issuer_id": "i2"},
    ]
    result = aggregate_exposure_by_issuer(positions)
    assert result["i1"] == 150.0
    assert result["i2"] == 25.0
