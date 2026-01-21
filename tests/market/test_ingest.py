from tradepilot.market.ingest import normalize_news_item


def test_normalize_news_item():
    item = {"headline": "ABC beats", "timestamp": "2026-01-20T10:00:00Z"}
    normalized = normalize_news_item(item)
    assert normalized["headline"] == "ABC beats"
