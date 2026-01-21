from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from tradepilot.db.models.ingest import IngestRefreshQueue
from tradepilot.metrics import QUEUE_DEPTH


@dataclass
class IngestQueue:
    session_factory: Callable[[], Session]

    def _update_depth(self, session: Session, data_type: str) -> None:
        count = (
            session.query(IngestRefreshQueue)
            .filter_by(status="pending", data_type=data_type)
            .count()
        )
        QUEUE_DEPTH.labels(data_type).set(count)

    def enqueue(self, tenant_id: str, book_id: str, data_type: str, reason: str) -> str:
        now = datetime.now(tz=timezone.utc).isoformat()
        dedupe_key = f"{tenant_id}:{book_id}:{data_type}"
        with self.session_factory() as session:
            existing = (
                session.query(IngestRefreshQueue)
                .filter_by(dedupe_key=dedupe_key)
                .filter(IngestRefreshQueue.status.in_(["pending", "processing"]))
                .first()
            )
            if existing:
                return existing.id
            job = IngestRefreshQueue(
                id=str(uuid4()),
                tenant_id=tenant_id,
                book_id=book_id,
                data_type=data_type,
                status="pending",
                attempts=0,
                next_attempt_at=now,
                last_error=None,
                dedupe_key=dedupe_key,
                reason=reason,
                created_at=now,
                updated_at=now,
            )
            session.add(job)
            session.commit()
            self._update_depth(session, data_type)
            return job.id

    def claim_due(self, data_type: str, now: str) -> Optional[dict]:
        with self.session_factory() as session:
            job = (
                session.query(IngestRefreshQueue)
                .filter_by(status="pending", data_type=data_type)
                .filter(IngestRefreshQueue.next_attempt_at <= now)
                .order_by(IngestRefreshQueue.next_attempt_at.asc())
                .with_for_update(skip_locked=True)
                .first()
            )
            if job is None:
                return None
            job.status = "processing"
            job.updated_at = now
            session.commit()
            self._update_depth(session, data_type)
            return {
                "id": job.id,
                "tenant_id": job.tenant_id,
                "book_id": job.book_id,
                "data_type": job.data_type,
                "reason": job.reason,
                "attempts": job.attempts,
            }

    def pending_count(self, tenant_id: str, book_id: str, data_type: str) -> int:
        with self.session_factory() as session:
            return (
                session.query(IngestRefreshQueue)
                .filter_by(tenant_id=tenant_id, book_id=book_id, data_type=data_type, status="pending")
                .count()
            )

    def mark_succeeded(self, job_id: str, now: str) -> None:
        with self.session_factory() as session:
            job = session.get(IngestRefreshQueue, job_id)
            if job is None:
                return
            job.status = "succeeded"
            job.updated_at = now
            session.commit()
            self._update_depth(session, job.data_type)

    def mark_failed(self, job_id: str, now: str, error: str, attempts: int) -> None:
        with self.session_factory() as session:
            job = session.get(IngestRefreshQueue, job_id)
            if job is None:
                return
            job.status = "failed"
            job.last_error = error
            job.attempts = attempts
            job.updated_at = now
            session.commit()
            self._update_depth(session, job.data_type)

    def reschedule(self, job_id: str, now: str, next_attempt_at: str, error: str, attempts: int) -> None:
        with self.session_factory() as session:
            job = session.get(IngestRefreshQueue, job_id)
            if job is None:
                return
            job.status = "pending"
            job.last_error = error
            job.attempts = attempts
            job.next_attempt_at = next_attempt_at
            job.updated_at = now
            session.commit()
            self._update_depth(session, job.data_type)
