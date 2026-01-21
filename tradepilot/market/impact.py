def compute_impact(positions: list[dict]) -> float:
    return sum(position.get("notional", 0) for position in positions)
