from fastapi.testclient import TestClient

from tradepilot.main import app


def test_stage_trade_endpoint():
    client = TestClient(app)
    response = client.post(
        "/api/v1/trades/stage",
        json={"symbol": "AAPL", "side": "buy", "quantity": 10},
    )
    assert response.status_code == 200
    assert response.json()["emsx_order_id"].startswith("emsx-")
