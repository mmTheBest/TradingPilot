from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from tradepilot.db.base import Base


class TradeOverride(Base):
    __tablename__ = "trade_overrides"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    book_id: Mapped[str] = mapped_column(String(36), nullable=False)
    trade_id: Mapped[str] = mapped_column(String(36), nullable=False)
    reason: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
