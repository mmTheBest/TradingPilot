from dataclasses import dataclass
from typing import Callable, Optional

from sqlalchemy.orm import Session

from tradepilot.db.models.positions import PositionsSnapshotFull


@dataclass
class QueryService:
    session_factory: Callable[[], Session]

    def get_book_summary(self, tenant_id: str, book_id: str) -> Optional[dict]:
        with self.session_factory() as session:
            snapshot = (
                session.query(PositionsSnapshotFull)
                .filter_by(tenant_id=tenant_id, book_id=book_id)
                .order_by(PositionsSnapshotFull.as_of_ts.desc())
                .first()
            )
            if snapshot is None:
                return None
            return {
                "tenant_id": tenant_id,
                "book_id": book_id,
                "as_of_ts": snapshot.as_of_ts,
                "net_exposure": snapshot.net_exposure,
                "gross_notional": snapshot.gross_notional,
            }
