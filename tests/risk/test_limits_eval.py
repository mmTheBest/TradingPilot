from tradepilot.risk.limits_eval import evaluate_limit


def test_absolute_limit_blocks():
    result = evaluate_limit(
        current_exposure=120,
        absolute_limit=100,
        relative_limit_pct=0.5,
        book_notional=1000,
    )
    assert result.status == "failed"
