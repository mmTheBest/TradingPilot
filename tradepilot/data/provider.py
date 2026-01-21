from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Optional, Protocol

from sqlalchemy.orm import Session

from tradepilot.db.models.fx import FxRateSnapshot
from tradepilot.db.models.limits import RiskLimitsSnapshotFull, RiskLimitsVersioned
from tradepilot.db.models.positions import PositionsSnapshotFull
from tradepilot.db.models.reference import SecurityMaster


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
    issuer_id: str
    sector_id: str
    issuer_exposure: float
    issuer_absolute_limit: float
    issuer_relative_limit_pct: float
    sector_exposure: float
    sector_absolute_limit: float
    sector_relative_limit_pct: float
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

            positions_rows = positions.snapshot_json or []
            symbols = {row.get("symbol") for row in positions_rows if row.get("symbol")}
            symbols.add(symbol)
            security_rows = session.query(SecurityMaster).filter(SecurityMaster.symbol.in_(symbols)).all()
            security_map = {row.symbol: row for row in security_rows}
            missing_symbols = symbols.difference(security_map.keys())
            if missing_symbols:
                missing = ", ".join(sorted(missing_symbols))
                raise DataProviderError(f"security master missing for symbols: {missing}")

            limits_snapshot = (
                session.query(RiskLimitsSnapshotFull)
                .filter_by(tenant_id=tenant_id, book_id=book_id)
                .order_by(RiskLimitsSnapshotFull.as_of_ts.desc())
                .first()
            )
            if limits_snapshot is None:
                limits = (
                    session.query(RiskLimitsVersioned)
                    .filter_by(tenant_id=tenant_id, book_id=book_id)
                    .order_by(RiskLimitsVersioned.effective_from.desc())
                    .first()
                )
                if limits is None:
                    raise DataProviderError("limits version not found")
                limits_age = _age_minutes(limits.effective_from)
                limits_version_id = limits.version_id
            else:
                limits_age = _age_minutes(limits_snapshot.as_of_ts)
                limits_version_id = limits_snapshot.version_id

            limits_rows = (
                session.query(RiskLimitsVersioned)
                .filter_by(tenant_id=tenant_id, book_id=book_id, version_id=limits_version_id)
                .all()
            )
            if not limits_rows:
                raise DataProviderError("limits snapshot version missing")
            base_limits = next((row for row in limits_rows if row.dimension == "book"), limits_rows[0])

            target_security = security_map[symbol]
            issuer_id = target_security.issuer_id
            sector_id = target_security.sector_id

            issuer_totals: dict[str, float] = defaultdict(float)
            sector_totals: dict[str, float] = defaultdict(float)
            for row in positions_rows:
                sec = security_map.get(row.get("symbol"))
                if sec is None:
                    raise DataProviderError("security master missing for positions snapshot")
                notional = float(row.get("quantity", 0)) * float(row.get("price", 0))
                gross_notional = abs(notional)
                issuer_totals[sec.issuer_id] += gross_notional
                sector_totals[sec.sector_id] += gross_notional

            issuer_limits = next(
                (
                    row
                    for row in limits_rows
                    if row.dimension == "issuer" and row.dimension_id == issuer_id
                ),
                None,
            )
            if issuer_limits is None:
                raise DataProviderError("issuer limits not found")

            sector_limits = next(
                (
                    row
                    for row in limits_rows
                    if row.dimension == "sector" and row.dimension_id == sector_id
                ),
                None,
            )
            if sector_limits is None:
                raise DataProviderError("sector limits not found")

            fx_snapshot = session.query(FxRateSnapshot).order_by(FxRateSnapshot.as_of_ts.desc()).first()

        positions_age = _age_minutes(positions.as_of_ts)

        return DataSnapshot(
            positions_age_minutes=positions_age,
            limits_age_minutes=limits_age,
            current_exposure=positions.net_exposure,
            absolute_limit=base_limits.absolute_limit,
            relative_limit_pct=base_limits.relative_limit_pct,
            book_notional=positions.gross_notional,
            adv=self.default_adv,
            positions_as_of_ts=positions.as_of_ts,
            limits_version_id=limits_version_id,
            issuer_id=issuer_id,
            sector_id=sector_id,
            issuer_exposure=issuer_totals.get(issuer_id, 0.0),
            issuer_absolute_limit=issuer_limits.absolute_limit,
            issuer_relative_limit_pct=issuer_limits.relative_limit_pct,
            sector_exposure=sector_totals.get(sector_id, 0.0),
            sector_absolute_limit=sector_limits.absolute_limit,
            sector_relative_limit_pct=sector_limits.relative_limit_pct,
            fx_rate_snapshot_id=fx_snapshot.snapshot_id if fx_snapshot else None,
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
