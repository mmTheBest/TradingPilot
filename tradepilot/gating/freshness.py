from dataclasses import dataclass


@dataclass
class GateResult:
    allowed: bool
    reason: str


class FreshnessGate:
    def __init__(self, positions_sla_minutes: int, limits_sla_minutes: int) -> None:
        self.positions_sla_minutes = positions_sla_minutes
        self.limits_sla_minutes = limits_sla_minutes

    def evaluate(self, positions_age_minutes: int, limits_age_minutes: int) -> GateResult:
        if positions_age_minutes > self.positions_sla_minutes:
            return GateResult(False, "positions_stale")
        if limits_age_minutes > self.limits_sla_minutes:
            return GateResult(False, "limits_stale")
        return GateResult(True, "fresh")
