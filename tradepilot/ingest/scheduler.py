from datetime import datetime, time
from zoneinfo import ZoneInfo

from tradepilot.config import settings


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def is_market_hours(now_ts: str) -> bool:
    parsed = _parse(now_ts)
    market_tz = ZoneInfo(settings.market_tz)
    local = parsed.astimezone(market_tz)
    if local.weekday() >= 5:
        return False
    open_parts = [int(part) for part in settings.market_open.split(":")]
    close_parts = [int(part) for part in settings.market_close.split(":")]
    market_open = time(open_parts[0], open_parts[1])
    market_close = time(close_parts[0], close_parts[1])
    return market_open <= local.time() <= market_close


def should_refresh(last_sync_ts: str, now_ts: str, sla_minutes: int) -> bool:
    delta = _parse(now_ts) - _parse(last_sync_ts)
    return delta.total_seconds() > sla_minutes * 60
