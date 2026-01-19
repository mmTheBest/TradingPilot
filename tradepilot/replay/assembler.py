def apply_deltas(base: dict, deltas: list[dict]) -> dict:
    current = dict(base)
    for item in sorted(deltas, key=lambda d: d["event_ts"]):
        current[item["symbol"]] = current.get(item["symbol"], 0) + item["delta"]
    return current
