from tradepilot.rationale.service import build_rationale


def test_build_rationale_includes_summary():
    rationale = build_rationale("buy", "AAPL")
    assert "AAPL" in rationale
