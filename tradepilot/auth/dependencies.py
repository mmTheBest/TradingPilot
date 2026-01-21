from datetime import datetime, timezone

from fastapi import Header, HTTPException

from tradepilot.db.models.auth import ApiKey
from tradepilot.db.session import SessionLocal


def require_api_key(x_api_key: str = Header(default="")):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="missing api key")
    with SessionLocal() as session:
        key = session.get(ApiKey, x_api_key)
        if key is None or key.revoked_at is not None:
            raise HTTPException(status_code=401, detail="invalid api key")
        key.last_used_at = datetime.now(tz=timezone.utc).isoformat()
        session.commit()
        return {"tenant_id": key.tenant_id, "role": key.role}
