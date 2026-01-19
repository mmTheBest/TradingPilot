from dataclasses import dataclass


@dataclass
class OverrideDecision:
    allowed: bool
    reason: str
    effective_cap: float


def evaluate_override(
    worst_case_reduces_exposure: bool,
    trade_notional: float,
    gross_notional: float,
    absolute_cap: float,
    relative_cap_pct: float,
    override_count: int,
    max_overrides_per_hour: int,
) -> OverrideDecision:
    effective_cap = min(absolute_cap, relative_cap_pct * gross_notional)
    if not worst_case_reduces_exposure:
        return OverrideDecision(False, "not_reduce_risk", effective_cap)
    if trade_notional > effective_cap:
        return OverrideDecision(False, "cap_exceeded", effective_cap)
    if override_count >= max_overrides_per_hour:
        return OverrideDecision(False, "rate_limited", effective_cap)
    return OverrideDecision(True, "approved", effective_cap)
