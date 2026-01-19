from tradepilot.gating.freshness import FreshnessGate


def test_positions_stale_blocks():
    gate = FreshnessGate(positions_sla_minutes=5, limits_sla_minutes=60)
    result = gate.evaluate(positions_age_minutes=6, limits_age_minutes=10)
    assert result.allowed is False
