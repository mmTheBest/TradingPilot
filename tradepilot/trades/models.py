from typing import Literal, Optional

from pydantic import BaseModel, Field

TradeSide = Literal["buy", "sell"]
TradeStatus = Literal["staged", "approved", "submitted", "rejected", "submit_failed"]


class TradeRequest(BaseModel):
    tenant_id: str
    book_id: str
    symbol: str
    side: TradeSide
    quantity: float = Field(gt=0)
    order_type: str = "market"
    limit_price: Optional[float] = None


class RiskCheckResult(BaseModel):
    check_name: str
    status: Literal["passed", "warning", "failed"]
    message: str


class StagedTrade(BaseModel):
    trade_id: str
    request: TradeRequest
    risk_checks: list[RiskCheckResult]
    status: TradeStatus
    positions_as_of_ts: str
    limits_version_id: str
    fx_rate_snapshot_id: Optional[str] = None
    emsx_order_id: Optional[str] = None
