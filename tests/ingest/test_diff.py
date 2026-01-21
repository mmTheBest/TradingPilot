from tradepilot.ingest.diff import diff_positions


def test_positions_diff_add_update_delete():
    prev = [
        {"symbol": "AAPL", "quantity": 10, "price": 100.0, "currency": "USD"},
        {"symbol": "MSFT", "quantity": 5, "price": 200.0, "currency": "USD"},
    ]
    new = [
        {"symbol": "AAPL", "quantity": 12, "price": 100.0, "currency": "USD"},
        {"symbol": "GOOG", "quantity": 1, "price": 300.0, "currency": "USD"},
    ]
    ops = diff_positions(prev, new, key_fields=["symbol"])
    assert {op["op"] for op in ops} == {"add", "update", "delete"}
