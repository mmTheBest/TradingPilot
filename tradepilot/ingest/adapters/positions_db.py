from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass
class PositionsDbAdapter:
    session_factory: Callable[[], Session]
    table_name: str = "positions_view"

    def fetch_positions(self, tenant_id: str, book_id: str) -> tuple[str, list[dict]]:
        query = text(
            f"""
            select symbol, quantity, price, currency, as_of_ts
            from {self.table_name}
            where tenant_id = :tenant_id and book_id = :book_id
            """
        )
        with self.session_factory() as session:
            rows = [
                dict(row)
                for row in session.execute(
                    query,
                    {"tenant_id": tenant_id, "book_id": book_id},
                ).mappings()
            ]
        if rows:
            as_of_ts = max(row["as_of_ts"] for row in rows)
        else:
            as_of_ts = datetime.now(tz=timezone.utc).isoformat()
        return as_of_ts, rows
