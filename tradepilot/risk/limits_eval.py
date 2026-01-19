from tradepilot.trades.models import RiskCheckResult


def evaluate_limit(
    current_exposure: float,
    absolute_limit: float,
    relative_limit_pct: float,
    book_notional: float,
) -> RiskCheckResult:
    if current_exposure > absolute_limit:
        return RiskCheckResult(check_name="absolute_limit", status="failed", message="absolute limit exceeded")
    if current_exposure > (relative_limit_pct * book_notional):
        return RiskCheckResult(check_name="relative_limit", status="failed", message="relative limit exceeded")
    return RiskCheckResult(check_name="limit_ok", status="passed", message="within limits")
