from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from tradepilot.db.models.overrides import TradeOverride


@dataclass
class OverrideRepository:
    session_factory: callable

    def record_override(self, tenant_id: str, book_id: str, trade_id: str, reason: str) -> None:
        now = datetime.now(tz=timezone.utc).isoformat()
        with self.session_factory() as session:
            session.add(
                TradeOverride(
                    id=str(uuid4()),
                    tenant_id=tenant_id,
                    book_id=book_id,
                    trade_id=trade_id,
                    reason=reason,
                    created_at=now,
                )
            )
            session.commit()

    def count_recent(self, tenant_id: str, book_id: str, window_minutes: int = 60) -> int:
        cutoff = datetime.now(tz=timezone.utc) - timedelta(minutes=window_minutes)
        cutoff_ts = cutoff.isoformat()
        with self.session_factory() as session:
            return (
                session.query(TradeOverride)
                .filter_by(tenant_id=tenant_id, book_id=book_id)
                .filter(TradeOverride.created_at >= cutoff_ts)
                .count()
            )
