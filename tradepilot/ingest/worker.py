from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from tradepilot.db.models.ingest import IngestRun
from tradepilot.ingest.adapters.base import FxAdapter, LimitsAdapter, PositionsAdapter
from tradepilot.ingest.canonical import hash_payload
from tradepilot.ingest.queue import IngestQueue
from tradepilot.ingest.repository import IngestRepository
from tradepilot.trades.submit_worker import RetryPolicy


@dataclass
class IngestWorker:
    session_factory: Callable[[], Session]
    queue: IngestQueue
    repository: IngestRepository
    positions_adapter: Optional[PositionsAdapter] = None
    limits_adapter: Optional[LimitsAdapter] = None
    fx_adapter: Optional[FxAdapter] = None
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)

    def run_once(self, data_type: str) -> int:
        now = _utc_now_iso()
        job = self.queue.claim_due(data_type=data_type, now=now)
        if job is None:
            return 0

        run_id = self._create_run(job, now)
        try:
            if data_type == "positions":
                if self.positions_adapter is None:
                    raise ValueError("positions adapter not configured")
                as_of_ts, rows = self.positions_adapter.fetch_positions(job["tenant_id"], job["book_id"])
                self.repository.record_positions_ingest(job["tenant_id"], job["book_id"], as_of_ts, job["reason"], rows)

                if self.fx_adapter is not None:
                    snapshot_id = str(uuid4())
                    pairs = _extract_pairs(rows, base_ccy="USD")
                    if pairs:
                        rates = self.fx_adapter.fetch_fx_snapshot(as_of_ts, pairs)
                        self.repository.record_fx_ingest(
                            job["tenant_id"],
                            job["book_id"],
                            as_of_ts,
                            "positions_sync",
                            rates,
                            snapshot_id,
                        )
                payload_hash = hash_payload(rows)
                row_count = len(rows)
            elif data_type == "limits":
                if self.limits_adapter is None:
                    raise ValueError("limits adapter not configured")
                as_of_ts, version_id, rows = self.limits_adapter.fetch_limits_version(job["tenant_id"], job["book_id"])
                self.repository.record_limits_ingest(
                    job["tenant_id"],
                    job["book_id"],
                    as_of_ts,
                    version_id,
                    job["reason"],
                    rows,
                )
                payload_hash = hash_payload(rows)
                row_count = len(rows)
            elif data_type == "fx":
                if self.fx_adapter is None:
                    raise ValueError("fx adapter not configured")
                rates = self.fx_adapter.fetch_fx_snapshot(now, [])
                self.repository.record_fx_ingest(
                    job["tenant_id"],
                    job["book_id"],
                    now,
                    job["reason"],
                    rates,
                    str(uuid4()),
                )
                as_of_ts = now
                payload_hash = hash_payload(rates)
                row_count = len(rates)
            else:
                raise ValueError(f"unknown data type: {data_type}")

            self._finish_run(run_id, now, "succeeded", as_of_ts, payload_hash, row_count, None)
            self.queue.mark_succeeded(job["id"], now)
        except Exception as exc:
            self._finish_run(run_id, now, "failed", None, None, None, str(exc))
            attempts = job["attempts"] + 1
            if attempts >= self.retry_policy.max_attempts:
                self.queue.mark_failed(job["id"], now, str(exc), attempts)
            else:
                delay = self.retry_policy.next_delay(attempts)
                next_attempt_at = (_utc_now() + delay).isoformat()
                self.queue.reschedule(job["id"], now, next_attempt_at, str(exc), attempts)
        return 1

    def _create_run(self, job: dict, now: str) -> str:
        run_id = str(uuid4())
        with self.session_factory() as session:
            session.add(
                IngestRun(
                    id=run_id,
                    tenant_id=job["tenant_id"],
                    book_id=job["book_id"],
                    data_type=job["data_type"],
                    started_at=now,
                    finished_at=None,
                    status="running",
                    as_of_ts=None,
                    payload_hash=None,
                    row_count=None,
                    error=None,
                )
            )
            session.commit()
        return run_id

    def _finish_run(
        self,
        run_id: str,
        finished_at: str,
        status: str,
        as_of_ts: Optional[str],
        payload_hash: Optional[str],
        row_count: Optional[int],
        error: Optional[str],
    ) -> None:
        with self.session_factory() as session:
            run = session.get(IngestRun, run_id)
            if run is None:
                return
            run.finished_at = finished_at
            run.status = status
            run.as_of_ts = as_of_ts
            run.payload_hash = payload_hash
            run.row_count = row_count
            run.error = error
            session.commit()


def _extract_pairs(rows: list[dict], base_ccy: str) -> list[tuple[str, str]]:
    pairs = {(base_ccy, row.get("currency", base_ccy)) for row in rows if row.get("currency")}
    return sorted(pair for pair in pairs if pair[0] != pair[1])


def _utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _utc_now_iso() -> str:
    return _utc_now().isoformat()
