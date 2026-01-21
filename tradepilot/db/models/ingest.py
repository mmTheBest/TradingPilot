from sqlalchemy import Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from tradepilot.db.base import Base


class IngestRun(Base):
    __tablename__ = "ingest_run"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    book_id: Mapped[str] = mapped_column(String(36), nullable=False)
    data_type: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[str] = mapped_column(String(32), nullable=False)
    finished_at: Mapped[str] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    as_of_ts: Mapped[str] = mapped_column(String(32), nullable=True)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=True)
    row_count: Mapped[int] = mapped_column(Integer, nullable=True)
    error: Mapped[str] = mapped_column(String(256), nullable=True)


class IngestRefreshQueue(Base):
    __tablename__ = "ingest_refresh_queue"
    __table_args__ = (
        UniqueConstraint("dedupe_key", name="uq_ingest_refresh_queue_dedupe"),
        Index("ix_ingest_refresh_queue_status", "status"),
        Index("ix_ingest_refresh_queue_next_attempt", "next_attempt_at"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    book_id: Mapped[str] = mapped_column(String(36), nullable=False)
    data_type: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    next_attempt_at: Mapped[str] = mapped_column(String(32), nullable=False)
    last_error: Mapped[str] = mapped_column(String(256), nullable=True)
    dedupe_key: Mapped[str] = mapped_column(String(128), nullable=False)
    reason: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False)
