from typing import Literal, Optional

from pydantic import BaseModel, Field

TradeSide = Literal["buy", "sell"]


class TradeRequest(BaseModel):
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
    emsx_order_id: Optional[str] = None
