import httpx

from tradepilot.ingest.adapters.reference_api import ReferenceApiAdapter


def test_reference_adapter_fetches_list():
    def handler(request):
        return httpx.Response(200, json=[{"symbol": "AAPL"}])

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    adapter = ReferenceApiAdapter(endpoint="http://example.com", client=client)
    rows = adapter.fetch_reference()
    assert rows[0]["symbol"] == "AAPL"
