import httpx

from tradepilot.ingest.adapters.fx_api import FxApiAdapter


def test_fx_api_adapter_parses_response():
    def handler(request):
        return httpx.Response(
            200,
            json={"rows": [{"vendor": "bg", "base_ccy": "USD", "quote_ccy": "EUR", "mid_rate": 1.1}]},
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    adapter = FxApiAdapter(endpoint="http://fx", client=client)

    rows = adapter.fetch_fx_snapshot("2026-01-20T10:00:00Z", [("USD", "EUR")])
    assert rows[0]["vendor"] == "bg"
