from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from sqlalchemy.orm import Session

from tradepilot.db.models.reference import SecurityMaster


@dataclass
class ReferenceRepository:
    session_factory: Callable[[], Session]

    def upsert_securities(self, rows: list[dict]) -> None:
        now = datetime.now(tz=timezone.utc).isoformat()
        with self.session_factory() as session:
            for row in rows:
                symbol = row.get("symbol")
                if not symbol:
                    continue
                existing = session.get(SecurityMaster, symbol)
                if existing is None:
                    session.add(
                        SecurityMaster(
                            symbol=symbol,
                            issuer_id=row.get("issuer_id", ""),
                            sector_id=row.get("sector_id", ""),
                            taxonomy_id=row.get("taxonomy_id", ""),
                            updated_at=row.get("updated_at", now),
                        )
                    )
                else:
                    existing.issuer_id = row.get("issuer_id", existing.issuer_id)
                    existing.sector_id = row.get("sector_id", existing.sector_id)
                    existing.taxonomy_id = row.get("taxonomy_id", existing.taxonomy_id)
                    existing.updated_at = row.get("updated_at", now)
            session.commit()

    def count(self) -> int:
        with self.session_factory() as session:
            return session.query(SecurityMaster).count()
