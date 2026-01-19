from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from tradepilot.db.base import Base


class RiskLimitsVersioned(Base):
    __tablename__ = "risk_limits_versioned"
    version_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    book_id: Mapped[str] = mapped_column(String(36), nullable=False)
    dimension: Mapped[str] = mapped_column(String(32), nullable=False)  # issuer|sector
    dimension_id: Mapped[str] = mapped_column(String(36), nullable=False)
    absolute_limit: Mapped[float] = mapped_column(nullable=False)
    relative_limit_pct: Mapped[float] = mapped_column(nullable=False)
    effective_from: Mapped[str] = mapped_column(String(32), nullable=False)
    effective_to: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)


class RiskLimitsSnapshotFull(Base):
    __tablename__ = "limits_snapshot_full"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    book_id: Mapped[str] = mapped_column(String(36), nullable=False)
    as_of_ts: Mapped[str] = mapped_column(String(32), nullable=False)


class RiskLimitsDelta(Base):
    __tablename__ = "limits_delta"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    book_id: Mapped[str] = mapped_column(String(36), nullable=False)
    version_id: Mapped[str] = mapped_column(String(36), nullable=False)
    event_ts: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[str] = mapped_column(String(64), nullable=False)
