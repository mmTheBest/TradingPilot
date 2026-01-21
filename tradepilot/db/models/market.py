from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from tradepilot.db.base import Base
from tradepilot.db.types import JSONB_COMPAT


class MarketNewsItem(Base):
    __tablename__ = "market_news_item"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    headline: Mapped[str] = mapped_column(String(512), nullable=False)
    timestamp: Mapped[str] = mapped_column(String(32), nullable=False)
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSONB_COMPAT, nullable=False)
