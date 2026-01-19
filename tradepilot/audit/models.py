import hashlib
import json
from dataclasses import dataclass, field


def hash_payload(payload: dict) -> str:
    data = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


@dataclass
class AuditEvent:
    event_type: str
    actor_id: str
    payload: dict
    input_hash: str = field(init=False)

    def __post_init__(self) -> None:
        self.input_hash = hash_payload(self.payload)
