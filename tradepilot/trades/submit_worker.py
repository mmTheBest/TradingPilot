from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import random
from typing import Callable, Optional

from sqlalchemy.orm import Session

from tradepilot.db.models.tradeflow import StagedTradeRecord, TradeSubmitQueue
from tradepilot.integrations.emsx import EmsxClient
from tradepilot.audit.service import DbAuditWriter


@dataclass
class RetryPolicy:
    max_attempts: int = 6

    def next_delay(self, attempt: int) -> timedelta:
        backoff_minutes = min(2 ** max(attempt - 1, 0), 30)
        jitter_seconds = random.randint(0, 30)
        return timedelta(minutes=backoff_minutes, seconds=jitter_seconds)


@dataclass
class SubmitWorker:
    session_factory: Callable[[], Session]
    emsx_client: EmsxClient
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    audit_writer: Optional[DbAuditWriter] = None

    def run_once(self) -> int:
        now = datetime.now(tz=timezone.utc)
        processed = 0
        with self.session_factory() as session:
            jobs = session.query(TradeSubmitQueue).filter_by(status="pending").all()
            for job in jobs:
                if _parse_timestamp(job.next_attempt_at) > now:
                    continue
                trade = session.get(StagedTradeRecord, job.trade_id)
                if trade is None or trade.emsx_order_id is None:
                    job.status = "failed"
                    job.last_error = "missing trade or EMSX order id"
                    job.updated_at = now.isoformat()
                    if trade is not None:
                        trade.status = "submit_failed"
                        self._audit(trade.tenant_id, "trade.submit_failed", trade, job.last_error, job.attempts)
                    processed += 1
                    continue
                try:
                    job.attempts += 1
                    self.emsx_client.submit_order(trade.emsx_order_id)
                    job.status = "submitted"
                    trade.status = "submitted"
                    job.updated_at = now.isoformat()
                    self._audit(trade.tenant_id, "trade.submitted", trade, None, job.attempts)
                except Exception as exc:
                    job.last_error = str(exc)
                    job.updated_at = now.isoformat()
                    if job.attempts >= self.retry_policy.max_attempts:
                        job.status = "failed"
                        trade.status = "submit_failed"
                        self._audit(trade.tenant_id, "trade.submit_failed", trade, job.last_error, job.attempts)
                    else:
                        delay = self.retry_policy.next_delay(job.attempts)
                        job.next_attempt_at = (now + delay).isoformat()
                        self._audit(trade.tenant_id, "trade.submit_retry", trade, job.last_error, job.attempts)
                processed += 1
            session.commit()
        return processed

    def _audit(
        self,
        tenant_id: str,
        event_type: str,
        trade: StagedTradeRecord,
        error: Optional[str],
        attempts: int,
    ) -> None:
        if self.audit_writer is None:
            return
        self.audit_writer.write(
            tenant_id=tenant_id,
            event_type=event_type,
            payload={
                "trade_id": trade.trade_id,
                "emsx_order_id": trade.emsx_order_id,
                "status": trade.status,
                "attempts": attempts,
                "error": error or "",
                "positions_as_of_ts": trade.positions_as_of_ts,
                "limits_version_id": trade.limits_version_id,
                "fx_rate_snapshot_id": trade.fx_rate_snapshot_id,
            },
        )


def _parse_timestamp(timestamp: str) -> datetime:
    if timestamp.endswith("Z"):
        timestamp = timestamp[:-1] + "+00:00"
    parsed = datetime.fromisoformat(timestamp)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
