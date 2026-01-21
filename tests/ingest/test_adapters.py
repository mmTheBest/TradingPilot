from tradepilot.ingest.adapters.base import PositionsAdapter
from tradepilot.ingest.adapters.fixtures import FixturePositionsAdapter


def test_fixture_positions_adapter_returns_rows():
    adapter: PositionsAdapter = FixturePositionsAdapter(
        as_of_ts="2026-01-20T10:00:00Z",
        rows=[{"symbol": "AAPL", "quantity": 10, "price": 100.0, "currency": "USD"}],
    )
    as_of_ts, rows = adapter.fetch_positions(tenant_id="t1", book_id="b1")
    assert as_of_ts == "2026-01-20T10:00:00Z"
    assert rows[0]["symbol"] == "AAPL"
