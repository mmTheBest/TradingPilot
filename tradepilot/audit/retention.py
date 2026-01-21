from tradepilot.db.models.ingest import IngestRun
from tradepilot.db.models.limits import RiskLimitsDelta, RiskLimitsSnapshotFull
from tradepilot.db.models.positions import PositionsDelta, PositionsSnapshotFull
from tradepilot.db.models.tradeflow import TradeApproval


def prune_positions_deltas(session_factory, cutoff_ts: str) -> int:
    with session_factory() as session:
        deleted = session.query(PositionsDelta).filter(PositionsDelta.event_ts < cutoff_ts).delete()
        session.commit()
        return deleted


def prune_positions_snapshots(session_factory, cutoff_ts: str) -> int:
    with session_factory() as session:
        deleted = session.query(PositionsSnapshotFull).filter(PositionsSnapshotFull.as_of_ts < cutoff_ts).delete()
        session.commit()
        return deleted


def prune_limits_snapshots(session_factory, cutoff_ts: str) -> int:
    with session_factory() as session:
        deleted = session.query(RiskLimitsSnapshotFull).filter(RiskLimitsSnapshotFull.as_of_ts < cutoff_ts).delete()
        session.commit()
        return deleted


def prune_limits_deltas(session_factory, cutoff_ts: str) -> int:
    with session_factory() as session:
        deleted = session.query(RiskLimitsDelta).filter(RiskLimitsDelta.event_ts < cutoff_ts).delete()
        session.commit()
        return deleted


def prune_ingest_runs(session_factory, cutoff_ts: str) -> int:
    with session_factory() as session:
        deleted = session.query(IngestRun).filter(IngestRun.started_at < cutoff_ts).delete()
        session.commit()
        return deleted


def prune_trade_approvals(session_factory, cutoff_ts: str) -> int:
    with session_factory() as session:
        deleted = session.query(TradeApproval).filter(TradeApproval.created_at < cutoff_ts).delete()
        session.commit()
        return deleted
