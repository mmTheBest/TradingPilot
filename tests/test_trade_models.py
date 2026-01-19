import pytest

from tradepilot.trades.models import TradeRequest


def test_trade_request_validates_side():
    with pytest.raises(ValueError):
        TradeRequest(symbol="AAPL", side="hold", quantity=10)
