from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from tradepilot.db.models.market import MarketNewsItem


@dataclass
class MarketNewsRepository:
    session_factory: callable

    def add_items(self, tenant_id: str, items: list[dict]) -> None:
        now = datetime.now(tz=timezone.utc).isoformat()
        with self.session_factory() as session:
            for item in items:
                session.add(
                    MarketNewsItem(
                        id=str(uuid4()),
                        tenant_id=tenant_id,
                        headline=item.get("headline", ""),
                        timestamp=item.get("timestamp", now),
                        source=item.get("source", ""),
                        payload_json=item,
                    )
                )
            session.commit()

    def count(self) -> int:
        with self.session_factory() as session:
            return session.query(MarketNewsItem).count()
