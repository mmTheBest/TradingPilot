from dataclasses import dataclass

from tradepilot.integrations.emsx import EmsxClient
from tradepilot.risk.checks import (
    check_best_execution_prompt,
    check_liquidity_slippage,
    check_position_limit,
)
from tradepilot.trades.models import RiskCheckResult, StagedTrade, TradeRequest


class RiskCheckFailed(Exception):
    pass


@dataclass
class TradeService:
    emsx_client: EmsxClient

    def stage_trade(
        self,
        request: TradeRequest,
        current_position: float,
        position_limit: float,
        adv: float,
    ) -> StagedTrade:
        checks: list[RiskCheckResult] = [
            check_position_limit(current_position, request.quantity, position_limit),
            check_liquidity_slippage(adv, request.quantity),
            check_best_execution_prompt(request.order_type),
        ]
        if any(check.status == "failed" for check in checks):
            raise RiskCheckFailed("risk checks failed")
        emsx_order_id = self.emsx_client.stage_order(request)
        return StagedTrade(
            trade_id=emsx_order_id,
            request=request,
            risk_checks=checks,
            emsx_order_id=emsx_order_id,
        )
