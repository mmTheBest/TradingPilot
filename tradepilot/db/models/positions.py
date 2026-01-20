from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from tradepilot.db.base import Base


class PositionsSnapshotFull(Base):
    __tablename__ = "positions_snapshot_full"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    book_id: Mapped[str] = mapped_column(String(36), nullable=False)
    as_of_ts: Mapped[str] = mapped_column(String(32), nullable=False)
    net_exposure: Mapped[float] = mapped_column(nullable=False)
    gross_notional: Mapped[float] = mapped_column(nullable=False)


class PositionsDelta(Base):
    __tablename__ = "positions_delta"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    book_id: Mapped[str] = mapped_column(String(36), nullable=False)
    event_ts: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[str] = mapped_column(String(64), nullable=False)
