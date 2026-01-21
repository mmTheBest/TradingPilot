from collections import defaultdict


def aggregate_exposure_by_issuer(rows: list[dict]) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for row in rows:
        totals[row["issuer_id"]] += abs(row["notional"])
    return dict(totals)
