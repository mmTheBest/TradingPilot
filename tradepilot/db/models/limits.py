from typing import Optional

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from tradepilot.db.base import Base
from tradepilot.db.types import JSONB_COMPAT


class RiskLimitsVersioned(Base):
    __tablename__ = "risk_limits_versioned"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "book_id",
            "version_id",
            "dimension",
            "dimension_id",
            "effective_from",
            name="uq_limits_version_row",
        ),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    version_id: Mapped[str] = mapped_column(String(36), nullable=False)
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
    version_id: Mapped[str] = mapped_column(String(36), nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)


class RiskLimitsDelta(Base):
    __tablename__ = "limits_delta"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    book_id: Mapped[str] = mapped_column(String(36), nullable=False)
    version_id: Mapped[str] = mapped_column(String(36), nullable=False)
    event_ts: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[str] = mapped_column(String(64), nullable=False)
    summary_json: Mapped[Optional[dict]] = mapped_column(JSONB_COMPAT, nullable=True)
