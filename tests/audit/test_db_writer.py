from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from tradepilot.audit.models import hash_payload
from tradepilot.audit.service import DbAuditWriter
from tradepilot.db.base import Base
from tradepilot.db.models.audit import AuditEvent


def test_audit_writer_persists_event():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    writer = DbAuditWriter(session_factory=SessionLocal)
    payload = {"trade_id": "trade-1"}
    writer.write(tenant_id="tenant-1", event_type="trade.approved", payload=payload)

    with SessionLocal() as session:
        row = session.query(AuditEvent).one()
        assert row.payload_hash == hash_payload(payload)
