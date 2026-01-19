import pytest

from tradepilot.integrations.emsx import FakeEmsxClient
from tradepilot.trades.models import TradeRequest
from tradepilot.trades.service import RiskCheckFailed, TradeService


def test_trade_service_blocks_on_failed_risk_check():
    service = TradeService(emsx_client=FakeEmsxClient())
    request = TradeRequest(symbol="AAPL", side="buy", quantity=200)
    with pytest.raises(RiskCheckFailed):
        service.stage_trade(request, current_position=900, position_limit=1000, adv=10000)
