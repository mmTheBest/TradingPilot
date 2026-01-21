from tradepilot.market.detect import detect_price_spike


def test_detect_price_spike_flags_large_move():
    result = detect_price_spike(change_pct=5.0, threshold=3.0)
    assert result is True
