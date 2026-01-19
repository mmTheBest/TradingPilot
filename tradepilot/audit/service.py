from dataclasses import dataclass, field

from tradepilot.audit.models import AuditEvent


@dataclass
class InMemoryAuditWriter:
    events: list[AuditEvent] = field(default_factory=list)

    def write(self, event: AuditEvent) -> None:
        self.events.append(event)
