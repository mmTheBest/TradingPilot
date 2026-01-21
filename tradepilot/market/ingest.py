from tradepilot.market.repository import MarketNewsRepository


def normalize_news_item(item: dict) -> dict:
    return {
        "headline": item.get("headline", ""),
        "timestamp": item.get("timestamp", ""),
        "source": item.get("source", ""),
    }


def ingest_news_items(repository: MarketNewsRepository, tenant_id: str, items: list[dict]) -> None:
    normalized = [normalize_news_item(item) | item for item in items]
    repository.add_items(tenant_id, normalized)
