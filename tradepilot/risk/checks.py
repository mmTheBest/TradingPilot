from tradepilot.trades.models import RiskCheckResult


def check_position_limit(current_position: float, proposed_quantity: float, limit: float) -> RiskCheckResult:
    projected = current_position + proposed_quantity
    if projected > limit:
        return RiskCheckResult(check_name="position_limit", status="failed", message="position limit exceeded")
    return RiskCheckResult(check_name="position_limit", status="passed", message="within limit")


def check_concentration_limit(current_notional: float, proposed_notional: float, limit: float) -> RiskCheckResult:
    projected = current_notional + proposed_notional
    if projected > limit:
        return RiskCheckResult(check_name="concentration_limit", status="failed", message="concentration limit exceeded")
    return RiskCheckResult(check_name="concentration_limit", status="passed", message="within limit")


def check_liquidity_slippage(adv: float, proposed_quantity: float, max_adv_pct: float = 0.1) -> RiskCheckResult:
    if adv <= 0:
        return RiskCheckResult(check_name="liquidity_slippage", status="warning", message="missing ADV data")
    if proposed_quantity / adv > max_adv_pct:
        return RiskCheckResult(check_name="liquidity_slippage", status="warning", message="order exceeds ADV threshold")
    return RiskCheckResult(check_name="liquidity_slippage", status="passed", message="liquidity ok")


def check_best_execution_prompt(order_type: str) -> RiskCheckResult:
    return RiskCheckResult(check_name="best_execution", status="warning", message="best execution confirmation required")


def check_dimension_limit(
    current: float,
    absolute_limit: float,
    relative_limit_pct: float,
    book_notional: float,
) -> RiskCheckResult:
    relative_limit = relative_limit_pct * book_notional
    if current > min(absolute_limit, relative_limit):
        return RiskCheckResult(check_name="dimension_limit", status="failed", message="limit breached")
    return RiskCheckResult(check_name="dimension_limit", status="passed", message="ok")
