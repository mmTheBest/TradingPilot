from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from tradepilot.db.base import Base


class IssuerMaster(Base):
    __tablename__ = "issuer_master"
    issuer_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)


class SectorTaxonomy(Base):
    __tablename__ = "sector_taxonomy"
    taxonomy_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    taxonomy_version: Mapped[str] = mapped_column(String(64), nullable=False)
    vendor: Mapped[str] = mapped_column(String(64), nullable=False)
    effective_from: Mapped[str] = mapped_column(String(32), nullable=False)


class SecurityMaster(Base):
    __tablename__ = "security_master"
    symbol: Mapped[str] = mapped_column(String(32), primary_key=True)
    issuer_id: Mapped[str] = mapped_column(String(36), nullable=False)
    sector_id: Mapped[str] = mapped_column(String(36), nullable=False)
    taxonomy_id: Mapped[str] = mapped_column(String(36), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
