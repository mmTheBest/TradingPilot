from tradepilot.integrations.emsx import FakeEmsxClient
from tradepilot.trades.models import TradeRequest


def test_fake_emsx_stages_order():
    client = FakeEmsxClient()
    request = TradeRequest(symbol="AAPL", side="buy", quantity=10)
    order_id = client.stage_order(request)
    assert order_id.startswith("emsx-")
