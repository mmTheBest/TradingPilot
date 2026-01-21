from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable
from uuid import uuid4

from sqlalchemy.orm import Session

from tradepilot.db.models.fx import FxRateSnapshot
from tradepilot.db.models.limits import RiskLimitsDelta, RiskLimitsSnapshotFull, RiskLimitsVersioned
from tradepilot.db.models.positions import PositionsDelta, PositionsSnapshotFull
from tradepilot.ingest.canonical import hash_payload
from tradepilot.ingest.diff import diff_positions


@dataclass
class IngestRepository:
    session_factory: Callable[[], Session]

    def record_positions_ingest(
        self,
        tenant_id: str,
        book_id: str,
        as_of_ts: str,
        reason: str,
        rows: list[dict],
    ) -> None:
        payload_hash = hash_payload(rows)
        net_exposure = sum(row["quantity"] * row["price"] for row in rows)
        gross_notional = sum(abs(row["quantity"] * row["price"]) for row in rows)
        with self.session_factory() as session:
            prev = (
                session.query(PositionsSnapshotFull)
                .filter_by(tenant_id=tenant_id, book_id=book_id)
                .order_by(PositionsSnapshotFull.as_of_ts.desc())
                .first()
            )
            prev_rows = prev.snapshot_json if prev else []
            ops = diff_positions(prev_rows, rows, key_fields=["symbol"])

            snapshot = PositionsSnapshotFull(
                id=str(uuid4()),
                tenant_id=tenant_id,
                book_id=book_id,
                as_of_ts=as_of_ts,
                net_exposure=net_exposure,
                gross_notional=gross_notional,
                snapshot_json=rows,
                payload_hash=payload_hash,
            )
            session.add(snapshot)

            if ops:
                delta = PositionsDelta(
                    id=str(uuid4()),
                    tenant_id=tenant_id,
                    book_id=book_id,
                    event_ts=as_of_ts,
                    reason=reason,
                    ops_json=ops,
                    payload_hash=payload_hash,
                    op_count=len(ops),
                )
                session.add(delta)

            session.commit()

    def record_limits_ingest(
        self,
        tenant_id: str,
        book_id: str,
        as_of_ts: str,
        version_id: str,
        reason: str,
        rows: list[dict],
    ) -> None:
        payload_hash = hash_payload(rows)
        with self.session_factory() as session:
            existing = (
                session.query(RiskLimitsVersioned)
                .filter_by(tenant_id=tenant_id, book_id=book_id, version_id=version_id)
                .first()
            )
            if existing is None:
                for row in rows:
                    session.add(
                        RiskLimitsVersioned(
                            id=str(uuid4()),
                            version_id=version_id,
                            tenant_id=tenant_id,
                            book_id=book_id,
                            dimension=row["dimension"],
                            dimension_id=row["dimension_id"],
                            absolute_limit=row["absolute_limit"],
                            relative_limit_pct=row["relative_limit_pct"],
                            effective_from=row["effective_from"],
                            effective_to=row.get("effective_to"),
                        )
                    )

            prev_snapshot = (
                session.query(RiskLimitsSnapshotFull)
                .filter_by(tenant_id=tenant_id, book_id=book_id)
                .order_by(RiskLimitsSnapshotFull.as_of_ts.desc())
                .first()
            )

            session.add(
                RiskLimitsSnapshotFull(
                    id=str(uuid4()),
                    tenant_id=tenant_id,
                    book_id=book_id,
                    as_of_ts=as_of_ts,
                    version_id=version_id,
                    payload_hash=payload_hash,
                )
            )

            if prev_snapshot is None or prev_snapshot.version_id != version_id:
                session.add(
                    RiskLimitsDelta(
                        id=str(uuid4()),
                        tenant_id=tenant_id,
                        book_id=book_id,
                        version_id=version_id,
                        event_ts=as_of_ts,
                        reason=reason,
                        summary_json={
                            "from_version": prev_snapshot.version_id if prev_snapshot else None,
                            "to_version": version_id,
                            "count": len(rows),
                        },
                    )
                )

            session.commit()

    def record_fx_ingest(
        self,
        tenant_id: str,
        book_id: str,
        as_of_ts: str,
        reason: str,
        rates: list[dict],
    ) -> None:
        with self.session_factory() as session:
            for rate in rates:
                session.add(
                    FxRateSnapshot(
                        id=str(uuid4()),
                        vendor=rate["vendor"],
                        as_of_ts=as_of_ts,
                        base_ccy=rate["base_ccy"],
                        quote_ccy=rate["quote_ccy"],
                        mid_rate=rate["mid_rate"],
                    )
                )
            session.commit()


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
