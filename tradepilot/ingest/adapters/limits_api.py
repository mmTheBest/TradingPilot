from dataclasses import dataclass
from typing import Optional

import httpx


@dataclass
class LimitsApiAdapter:
    endpoint: str
    client: Optional[httpx.Client] = None

    def fetch_limits_version(self, tenant_id: str, book_id: str) -> tuple[str, str, list[dict]]:
        payload = {"tenant_id": tenant_id, "book_id": book_id}
        if self.client is None:
            with httpx.Client() as client:
                resp = client.post(f"{self.endpoint}/limits", json=payload, timeout=10)
        else:
            resp = self.client.post(f"{self.endpoint}/limits", json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data["as_of_ts"], data["version_id"], data["rows"]
