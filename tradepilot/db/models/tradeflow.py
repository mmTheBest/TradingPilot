from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from tradepilot.db.base import Base


class StagedTradeRecord(Base):
    __tablename__ = "staged_trades"
    trade_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    book_id: Mapped[str] = mapped_column(String(36), nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    side: Mapped[str] = mapped_column(String(8), nullable=False)
    quantity: Mapped[float] = mapped_column(nullable=False)
    order_type: Mapped[str] = mapped_column(String(16), nullable=False)
    limit_price: Mapped[Optional[float]] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    emsx_order_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    positions_as_of_ts: Mapped[str] = mapped_column(String(32), nullable=False)
    limits_version_id: Mapped[str] = mapped_column(String(36), nullable=False)
    fx_rate_snapshot_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)


class TradeApproval(Base):
    __tablename__ = "trade_approvals"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    trade_id: Mapped[str] = mapped_column(String(36), nullable=False)
    action: Mapped[str] = mapped_column(String(16), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    slack_user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    approver_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    approver_effective_from: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    approver_effective_to: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)


class TradeSubmitQueue(Base):
    __tablename__ = "trade_submit_queue"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    trade_id: Mapped[str] = mapped_column(String(36), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    attempts: Mapped[int] = mapped_column(nullable=False)
    next_attempt_at: Mapped[str] = mapped_column(String(32), nullable=False)
    last_error: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)


class SlackApprover(Base):
    __tablename__ = "slack_approvers"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    slack_user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    effective_from: Mapped[str] = mapped_column(String(32), nullable=False)
    effective_to: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    added_by: Mapped[str] = mapped_column(String(64), nullable=False)
    added_at: Mapped[str] = mapped_column(String(32), nullable=False)
