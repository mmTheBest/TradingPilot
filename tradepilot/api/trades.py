from fastapi import APIRouter, Depends

from tradepilot.data.provider import DbDataProvider
from tradepilot.db.session import SessionLocal
from tradepilot.integrations.emsx import FakeEmsxClient
from tradepilot.trades.models import TradeRequest
from tradepilot.trades.repository import TradeRepository
from tradepilot.trades.service import TradeService

router = APIRouter()


def get_trade_service() -> TradeService:
    provider = DbDataProvider(session_factory=SessionLocal)
    repository = TradeRepository(session_factory=SessionLocal)
    return TradeService(emsx_client=FakeEmsxClient(), data_provider=provider, repository=repository)


@router.post("/api/v1/trades/stage")
def stage_trade(request: TradeRequest, service: TradeService = Depends(get_trade_service)):
    staged = service.stage_trade(request)
    return staged.model_dump()


@router.post("/api/v1/trades/{trade_id}/approve")
def approve_trade(trade_id: str):
    return {"status": "approved", "trade_id": trade_id}


@router.post("/api/v1/trades/{trade_id}/reject")
def reject_trade(trade_id: str):
    return {"status": "rejected", "trade_id": trade_id}
