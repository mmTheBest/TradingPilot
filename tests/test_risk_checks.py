from tradepilot.risk.checks import check_position_limit


def test_position_limit_fails_when_exceeded():
    result = check_position_limit(current_position=900, proposed_quantity=200, limit=1000)
    assert result.status == "failed"
