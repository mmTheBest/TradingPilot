from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tradepilot.data.provider import DbDataProvider
from tradepilot.db.base import Base
from tradepilot.db.models.fx import FxRateSnapshot
from tradepilot.db.models.limits import RiskLimitsSnapshotFull, RiskLimitsVersioned
from tradepilot.db.models.positions import PositionsSnapshotFull


def test_db_provider_returns_latest_snapshot():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    now = datetime.now(tz=timezone.utc)
    positions_ts = (now - timedelta(minutes=2)).isoformat()
    limits_ts = (now - timedelta(minutes=3)).isoformat()
    fx_ts = (now - timedelta(minutes=1)).isoformat()

    with SessionLocal() as session:
        session.add(
            PositionsSnapshotFull(
                id="pos-1",
                tenant_id="tenant-1",
                book_id="book-1",
                as_of_ts=positions_ts,
                net_exposure=250.0,
                gross_notional=1000.0,
                snapshot_json=[],
                payload_hash="positions-hash",
            )
        )
        session.add(
            RiskLimitsVersioned(
                id="limits-row-1",
                version_id="limits-1",
                tenant_id="tenant-1",
                book_id="book-1",
                dimension="issuer",
                dimension_id="issuer-1",
                absolute_limit=500.0,
                relative_limit_pct=0.2,
                effective_from=limits_ts,
                effective_to=None,
            )
        )
        session.add(
            FxRateSnapshot(
                id="fx-1",
                vendor="vendor",
                as_of_ts=fx_ts,
                base_ccy="USD",
                quote_ccy="USD",
                mid_rate=1.0,
            )
        )
        session.commit()

    provider = DbDataProvider(session_factory=SessionLocal)
    snapshot = provider.get_snapshot(tenant_id="tenant-1", book_id="book-1", symbol="AAPL")

    assert snapshot.current_exposure == 250.0
    assert snapshot.book_notional == 1000.0
    assert snapshot.absolute_limit == 500.0
    assert snapshot.relative_limit_pct == 0.2
    assert snapshot.positions_as_of_ts == positions_ts
    assert snapshot.limits_version_id == "limits-1"
    assert snapshot.fx_rate_snapshot_id == "fx-1"
    assert snapshot.positions_age_minutes >= 2
    assert snapshot.limits_age_minutes >= 3


def test_db_provider_limits_age_uses_snapshot_as_of():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    now = datetime.now(tz=timezone.utc)
    limits_ts = (now - timedelta(minutes=7)).isoformat()

    with SessionLocal() as session:
        session.add(
            PositionsSnapshotFull(
                id="pos-1",
                tenant_id="tenant-1",
                book_id="book-1",
                as_of_ts=now.isoformat(),
                net_exposure=0.0,
                gross_notional=100.0,
                snapshot_json=[],
                payload_hash="pos-hash",
            )
        )
        session.add(
            RiskLimitsVersioned(
                id="limits-row-1",
                version_id="limits-1",
                tenant_id="tenant-1",
                book_id="book-1",
                dimension="issuer",
                dimension_id="issuer-1",
                absolute_limit=100.0,
                relative_limit_pct=0.1,
                effective_from=(now - timedelta(days=1)).isoformat(),
                effective_to=None,
            )
        )
        session.add(
            RiskLimitsSnapshotFull(
                id="snap-1",
                tenant_id="tenant-1",
                book_id="book-1",
                as_of_ts=limits_ts,
                version_id="limits-1",
                payload_hash="limits-hash",
            )
        )
        session.commit()

    provider = DbDataProvider(session_factory=SessionLocal)
    snapshot = provider.get_snapshot(tenant_id="tenant-1", book_id="book-1", symbol="AAPL")

    assert snapshot.limits_version_id == "limits-1"
    assert snapshot.limits_age_minutes >= 7
