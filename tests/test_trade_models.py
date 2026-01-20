import pytest
from pydantic import ValidationError

from tradepilot.trades.models import TradeRequest


def test_trade_request_validates_side():
    with pytest.raises(ValueError):
        TradeRequest(tenant_id="tenant-1", book_id="book-1", symbol="AAPL", side="hold", quantity=10)


def test_trade_request_requires_book_id():
    with pytest.raises(ValidationError):
        TradeRequest(tenant_id="tenant-1", symbol="AAPL", side="buy", quantity=10)
