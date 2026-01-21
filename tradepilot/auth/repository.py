from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from tradepilot.db.models.auth import ApiKey


@dataclass
class ApiKeyRepository:
    session_factory: callable

    def create_key(self, tenant_id: str, role: str, owner: str) -> str:
        key_id = str(uuid4())
        with self.session_factory() as session:
            session.add(
                ApiKey(
                    id=key_id,
                    tenant_id=tenant_id,
                    role=role,
                    owner=owner,
                    key_hash=key_id,
                    revoked_at=None,
                    last_used_at=None,
                    created_at=datetime.now(tz=timezone.utc).isoformat(),
                )
            )
            session.commit()
        return key_id

    def get_key(self, key_id: str):
        with self.session_factory() as session:
            return session.get(ApiKey, key_id)
