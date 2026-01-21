from dataclasses import dataclass
from typing import Callable

from sqlalchemy.orm import Session

from tradepilot.db.models.book import Book
from tradepilot.db.models.ingest import IngestRun
from tradepilot.ingest.queue import IngestQueue
from tradepilot.ingest.scheduler import is_market_hours, should_refresh


@dataclass
class IngestEnqueuer:
    session_factory: Callable[[], Session]
    queue: IngestQueue
    positions_sla_minutes: int = 5
    positions_sla_off_hours: int = 15
    limits_sla_minutes: int = 60
    reference_sla_minutes: int = 1440

    def enqueue_due(self, now_ts: str) -> int:
        enqueued = 0
        with self.session_factory() as session:
            books = session.query(Book).all()
            for book in books:
                positions_sla = self.positions_sla_minutes
                if not is_market_hours(now_ts):
                    positions_sla = self.positions_sla_off_hours

                last_positions = _last_success_ts(session, book.tenant_id, book.id, "positions")
                if last_positions is None or should_refresh(last_positions, now_ts, positions_sla):
                    self.queue.enqueue(book.tenant_id, book.id, "positions", reason="scheduled")
                    enqueued += 1

                last_limits = _last_success_ts(session, book.tenant_id, book.id, "limits")
                if last_limits is None or should_refresh(last_limits, now_ts, self.limits_sla_minutes):
                    self.queue.enqueue(book.tenant_id, book.id, "limits", reason="scheduled")
                    enqueued += 1

                last_reference = _last_success_ts(session, book.tenant_id, book.id, "reference")
                if last_reference is None or should_refresh(last_reference, now_ts, self.reference_sla_minutes):
                    self.queue.enqueue(book.tenant_id, book.id, "reference", reason="scheduled")
                    enqueued += 1

        return enqueued


def _last_success_ts(session: Session, tenant_id: str, book_id: str, data_type: str) -> str | None:
    run = (
        session.query(IngestRun)
        .filter_by(tenant_id=tenant_id, book_id=book_id, data_type=data_type, status="succeeded")
        .order_by(IngestRun.finished_at.desc())
        .first()
    )
    return run.finished_at if run else None
