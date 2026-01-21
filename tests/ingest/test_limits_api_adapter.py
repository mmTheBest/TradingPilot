import httpx

from tradepilot.ingest.adapters.limits_api import LimitsApiAdapter


def test_limits_api_adapter_parses_response():
    def handler(request):
        return httpx.Response(
            200,
            json={
                "as_of_ts": "2026-01-20T10:00:00Z",
                "version_id": "v1",
                "rows": [
                    {
                        "dimension": "issuer",
                        "dimension_id": "i1",
                        "absolute_limit": 100,
                        "relative_limit_pct": 0.1,
                        "effective_from": "2026-01-20T10:00:00Z",
                    }
                ],
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    adapter = LimitsApiAdapter(endpoint="http://limits", client=client)

    as_of_ts, version_id, rows = adapter.fetch_limits_version("t1", "b1")
    assert version_id == "v1"
    assert as_of_ts == "2026-01-20T10:00:00Z"
    assert rows[0]["dimension"] == "issuer"
