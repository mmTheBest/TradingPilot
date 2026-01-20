from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Optional, Protocol

from sqlalchemy.orm import Session

from tradepilot.db.models.fx import FxRateSnapshot
from tradepilot.db.models.limits import RiskLimitsVersioned
from tradepilot.db.models.positions import PositionsSnapshotFull


@dataclass(frozen=True)
class DataSnapshot:
    positions_age_minutes: int
    limits_age_minutes: int
    current_exposure: float
    absolute_limit: float
    relative_limit_pct: float
    book_notional: float
    adv: float
    positions_as_of_ts: str
    limits_version_id: str
    fx_rate_snapshot_id: Optional[str] = None


class DataProvider(Protocol):
    def get_snapshot(self, tenant_id: str, book_id: str, symbol: str) -> DataSnapshot:
        raise NotImplementedError


class DataProviderError(Exception):
    pass


@dataclass
class InMemoryDataProvider:
    snapshot: DataSnapshot

    def get_snapshot(self, tenant_id: str, book_id: str, symbol: str) -> DataSnapshot:
        return self.snapshot


@dataclass
class DbDataProvider:
    session_factory: Callable[[], Session]
    default_adv: float = 0.0

    def get_snapshot(self, tenant_id: str, book_id: str, symbol: str) -> DataSnapshot:
        with self.session_factory() as session:
            positions = (
                session.query(PositionsSnapshotFull)
                .filter_by(tenant_id=tenant_id, book_id=book_id)
                .order_by(PositionsSnapshotFull.as_of_ts.desc())
                .first()
            )
            if positions is None:
                raise DataProviderError("positions snapshot not found")

            limits = (
                session.query(RiskLimitsVersioned)
                .filter_by(tenant_id=tenant_id, book_id=book_id)
                .order_by(RiskLimitsVersioned.effective_from.desc())
                .first()
            )
            if limits is None:
                raise DataProviderError("limits version not found")

            fx_snapshot = session.query(FxRateSnapshot).order_by(FxRateSnapshot.as_of_ts.desc()).first()

        positions_age = _age_minutes(positions.as_of_ts)
        limits_age = _age_minutes(limits.effective_from)

        return DataSnapshot(
            positions_age_minutes=positions_age,
            limits_age_minutes=limits_age,
            current_exposure=positions.net_exposure,
            absolute_limit=limits.absolute_limit,
            relative_limit_pct=limits.relative_limit_pct,
            book_notional=positions.gross_notional,
            adv=self.default_adv,
            positions_as_of_ts=positions.as_of_ts,
            limits_version_id=limits.version_id,
            fx_rate_snapshot_id=fx_snapshot.id if fx_snapshot else None,
        )


def _age_minutes(timestamp: str) -> int:
    now = datetime.now(tz=timezone.utc)
    parsed = _parse_timestamp(timestamp)
    delta = now - parsed
    if delta.total_seconds() < 0:
        return 0
    return int(delta.total_seconds() // 60)


def _parse_timestamp(timestamp: str) -> datetime:
    if timestamp.endswith("Z"):
        timestamp = timestamp[:-1] + "+00:00"
    parsed = datetime.fromisoformat(timestamp)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
