from dataclasses import dataclass

from tradepilot.data.provider import DataProvider, DataProviderError
from tradepilot.gating.freshness import FreshnessGate
from tradepilot.integrations.emsx import EmsxClient
from tradepilot.risk.checks import check_best_execution_prompt, check_dimension_limit, check_liquidity_slippage
from tradepilot.risk.limits_eval import evaluate_limit
from tradepilot.trades.models import RiskCheckResult, StagedTrade, TradeRequest
from tradepilot.trades.repository import TradeRepository


class RiskCheckFailed(Exception):
    pass


@dataclass
class TradeService:
    emsx_client: EmsxClient
    data_provider: DataProvider
    repository: TradeRepository
    positions_sla_minutes: int = 5
    limits_sla_minutes: int = 60
    ingest_queue: object | None = None

    def stage_trade(self, request: TradeRequest) -> StagedTrade:
        try:
            snapshot = self.data_provider.get_snapshot(
                tenant_id=request.tenant_id,
                book_id=request.book_id,
                symbol=request.symbol,
            )
        except DataProviderError as exc:
            raise RiskCheckFailed(f"data provider error: {exc}") from exc
        gate = FreshnessGate(
            positions_sla_minutes=self.positions_sla_minutes,
            limits_sla_minutes=self.limits_sla_minutes,
        )
        gate_result = gate.evaluate(snapshot.positions_age_minutes, snapshot.limits_age_minutes)
        if not gate_result.allowed:
            if self.ingest_queue is not None:
                self.ingest_queue.enqueue(request.tenant_id, request.book_id, "positions", reason="stale_gate")
                self.ingest_queue.enqueue(request.tenant_id, request.book_id, "limits", reason="stale_gate")
            raise RiskCheckFailed(f"freshness gate blocked: {gate_result.reason}")

        projected_exposure = snapshot.current_exposure + request.quantity
        projected_issuer = snapshot.issuer_exposure + request.quantity
        projected_sector = snapshot.sector_exposure + request.quantity
        checks: list[RiskCheckResult] = [
            evaluate_limit(
                projected_exposure,
                snapshot.absolute_limit,
                snapshot.relative_limit_pct,
                snapshot.book_notional,
            ),
            check_dimension_limit(
                projected_issuer,
                snapshot.issuer_absolute_limit,
                snapshot.issuer_relative_limit_pct,
                snapshot.book_notional,
            ),
            check_dimension_limit(
                projected_sector,
                snapshot.sector_absolute_limit,
                snapshot.sector_relative_limit_pct,
                snapshot.book_notional,
            ),
            check_liquidity_slippage(snapshot.adv, request.quantity),
            check_best_execution_prompt(request.order_type),
        ]
        if any(check.status == "failed" for check in checks):
            raise RiskCheckFailed("risk checks failed")
        emsx_order_id = self.emsx_client.stage_order(request)
        trade_id = self.repository.create_staged_trade(
            tenant_id=request.tenant_id,
            book_id=request.book_id,
            symbol=request.symbol,
            side=request.side,
            quantity=request.quantity,
            order_type=request.order_type,
            limit_price=request.limit_price,
            status="staged",
            emsx_order_id=emsx_order_id,
            positions_as_of_ts=snapshot.positions_as_of_ts,
            limits_version_id=snapshot.limits_version_id,
            fx_rate_snapshot_id=snapshot.fx_rate_snapshot_id,
        )
        return StagedTrade(
            trade_id=trade_id,
            request=request,
            risk_checks=checks,
            status="staged",
            positions_as_of_ts=snapshot.positions_as_of_ts,
            limits_version_id=snapshot.limits_version_id,
            fx_rate_snapshot_id=snapshot.fx_rate_snapshot_id,
            emsx_order_id=emsx_order_id,
        )
