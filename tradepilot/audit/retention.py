from tradepilot.db.models.positions import PositionsDelta


def prune_positions_deltas(session_factory, cutoff_ts: str) -> int:
    with session_factory() as session:
        deleted = session.query(PositionsDelta).filter(PositionsDelta.event_ts < cutoff_ts).delete()
        session.commit()
        return deleted
