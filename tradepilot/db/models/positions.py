from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from tradepilot.db.base import Base
from tradepilot.db.types import JSONB_COMPAT


class PositionsSnapshotFull(Base):
    __tablename__ = "positions_snapshot_full"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    book_id: Mapped[str] = mapped_column(String(36), nullable=False)
    as_of_ts: Mapped[str] = mapped_column(String(32), nullable=False)
    net_exposure: Mapped[float] = mapped_column(nullable=False)
    gross_notional: Mapped[float] = mapped_column(nullable=False)
    snapshot_json: Mapped[list[dict]] = mapped_column(JSONB_COMPAT, nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)


class PositionsDelta(Base):
    __tablename__ = "positions_delta"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    book_id: Mapped[str] = mapped_column(String(36), nullable=False)
    event_ts: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[str] = mapped_column(String(64), nullable=False)
    ops_json: Mapped[list[dict]] = mapped_column(JSONB_COMPAT, nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    op_count: Mapped[int] = mapped_column(Integer, nullable=False)
