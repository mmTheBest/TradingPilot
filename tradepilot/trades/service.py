from dataclasses import dataclass

from tradepilot.config import settings
from tradepilot.data.provider import DataProvider, DataProviderError
from tradepilot.gating.freshness import FreshnessGate
from tradepilot.gating.override import evaluate_override
from tradepilot.integrations.emsx import EmsxClient
from tradepilot.risk.checks import check_best_execution_prompt, check_dimension_limit, check_liquidity_slippage
from tradepilot.risk.limits_eval import evaluate_limit
from tradepilot.trades.models import RiskCheckResult, StagedTrade, TradeRequest
from tradepilot.trades.override_repository import OverrideRepository
from tradepilot.trades.repository import TradeRepository


class RiskCheckFailed(Exception):
    pass


@dataclass
class TradeService:
    emsx_client: EmsxClient
    data_provider: DataProvider
    repository: TradeRepository
    override_repository: OverrideRepository | None = None
    positions_sla_minutes: int = 5
    limits_sla_minutes: int = 60
    ingest_queue: object | None = None

    def stage_trade(self, request: TradeRequest, actor_role: str | None = None) -> StagedTrade:
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
            if not request.override_requested:
                raise RiskCheckFailed(f"freshness gate blocked: {gate_result.reason}")
            if actor_role not in {"OPS", "RISK"}:
                raise RiskCheckFailed("override requires OPS or RISK role")

        price = request.price or request.limit_price or snapshot.symbol_price
        if price is None:
            raise RiskCheckFailed("missing price for notional calculation")
        side_sign = 1 if request.side == "buy" else -1
        trade_notional = price * request.quantity * side_sign

        projected_exposure = snapshot.current_exposure + trade_notional
        projected_issuer = (
            snapshot.issuer_exposure
            - abs(snapshot.symbol_notional)
            + abs(snapshot.symbol_notional + trade_notional)
        )
        projected_sector = (
            snapshot.sector_exposure
            - abs(snapshot.symbol_notional)
            + abs(snapshot.symbol_notional + trade_notional)
        )
        if gate_result.allowed is False and request.override_requested:
            override_count = 0
            if self.override_repository is not None:
                override_count = self.override_repository.count_recent(request.tenant_id, request.book_id)
            decision = evaluate_override(
                worst_case_reduces_exposure=(trade_notional < 0),
                trade_notional=abs(trade_notional),
                gross_notional=snapshot.book_notional,
                absolute_cap=settings.override_absolute_cap,
                relative_cap_pct=settings.override_relative_cap_pct,
                override_count=override_count,
                max_overrides_per_hour=settings.override_max_per_hour,
            )
            if not decision.allowed:
                raise RiskCheckFailed(f"override rejected: {decision.reason}")
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
        if gate_result.allowed is False and request.override_requested and self.override_repository is not None:
            self.override_repository.record_override(
                tenant_id=request.tenant_id,
                book_id=request.book_id,
                trade_id=trade_id,
                reason=request.override_reason or "override",
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
