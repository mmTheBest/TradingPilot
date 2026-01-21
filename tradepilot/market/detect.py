def detect_price_spike(change_pct: float, threshold: float) -> bool:
    return change_pct >= threshold
