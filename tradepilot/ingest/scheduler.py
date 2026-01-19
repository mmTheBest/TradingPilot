from datetime import datetime


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def should_refresh(last_sync_ts: str, now_ts: str, sla_minutes: int) -> bool:
    delta = _parse(now_ts) - _parse(last_sync_ts)
    return delta.total_seconds() > sla_minutes * 60
