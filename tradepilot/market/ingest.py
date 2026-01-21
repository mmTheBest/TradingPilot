def normalize_news_item(item: dict) -> dict:
    return {
        "headline": item.get("headline", ""),
        "timestamp": item.get("timestamp", ""),
    }
