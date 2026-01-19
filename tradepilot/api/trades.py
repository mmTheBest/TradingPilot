from fastapi import APIRouter

from tradepilot.integrations.emsx import FakeEmsxClient
from tradepilot.trades.models import TradeRequest
from tradepilot.trades.service import TradeService

router = APIRouter()
service = TradeService(emsx_client=FakeEmsxClient())


@router.post("/api/v1/trades/stage")
def stage_trade(request: TradeRequest):
    staged = service.stage_trade(
        request,
        current_position=0,
        position_limit=1_000_000,
        adv=1_000_000,
    )
    return staged.model_dump()


@router.post("/api/v1/trades/{trade_id}/approve")
def approve_trade(trade_id: str):
    return {"status": "approved", "trade_id": trade_id}


@router.post("/api/v1/trades/{trade_id}/reject")
def reject_trade(trade_id: str):
    return {"status": "rejected", "trade_id": trade_id}
