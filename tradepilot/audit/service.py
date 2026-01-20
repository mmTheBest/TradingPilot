from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable
from uuid import uuid4

from sqlalchemy.orm import Session

from tradepilot.audit.models import AuditEvent
from tradepilot.audit.models import hash_payload
from tradepilot.db.models.audit import AuditEvent as DbAuditEvent


@dataclass
class InMemoryAuditWriter:
    events: list[AuditEvent] = field(default_factory=list)

    def write(self, event: AuditEvent) -> None:
        self.events.append(event)


@dataclass
class DbAuditWriter:
    session_factory: Callable[[], Session]

    def write(self, tenant_id: str, event_type: str, payload: dict) -> None:
        event = DbAuditEvent(
            id=str(uuid4()),
            tenant_id=tenant_id,
            event_type=event_type,
            payload_hash=hash_payload(payload),
            as_of_ts=datetime.now(tz=timezone.utc).isoformat(),
        )
        with self.session_factory() as session:
            session.add(event)
            session.commit()
