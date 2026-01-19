from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from tradepilot.db.base import Base


class FxRateSnapshot(Base):
    __tablename__ = "fx_rate_snapshot"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    vendor: Mapped[str] = mapped_column(String(64), nullable=False)
    as_of_ts: Mapped[str] = mapped_column(String(32), nullable=False)
    base_ccy: Mapped[str] = mapped_column(String(3), nullable=False)
    quote_ccy: Mapped[str] = mapped_column(String(3), nullable=False)
    mid_rate: Mapped[float] = mapped_column(nullable=False)
