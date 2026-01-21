from tradepilot.risk.checks import check_dimension_limit


def test_dimension_limit_blocks_when_over():
    result = check_dimension_limit(current=120.0, absolute_limit=100.0, relative_limit_pct=0.1, book_notional=500.0)
    assert result.status == "failed"
