from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from tradepilot.db.base import Base


class Book(Base):
    __tablename__ = "books"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    portfolio_id: Mapped[str] = mapped_column(String(36), nullable=True)
    desk_id: Mapped[str] = mapped_column(String(36), nullable=True)
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False)
