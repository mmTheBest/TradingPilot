from tradepilot.gating.override import evaluate_override


def test_override_blocks_if_not_reduce_risk():
    decision = evaluate_override(
        worst_case_reduces_exposure=False,
        trade_notional=1_000,
        gross_notional=100_000,
        absolute_cap=5_000,
        relative_cap_pct=0.01,
        override_count=0,
        max_overrides_per_hour=3,
    )
    assert decision.allowed is False


def test_override_allows_when_reducing_and_below_caps():
    decision = evaluate_override(
        worst_case_reduces_exposure=True,
        trade_notional=1_000,
        gross_notional=100_000,
        absolute_cap=5_000,
        relative_cap_pct=0.02,
        override_count=0,
        max_overrides_per_hour=3,
    )
    assert decision.allowed is True
