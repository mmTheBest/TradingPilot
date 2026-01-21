from dataclasses import dataclass
from typing import Optional

import httpx


@dataclass
class FxApiAdapter:
    endpoint: str
    client: Optional[httpx.Client] = None

    def fetch_fx_snapshot(self, as_of_ts: str, pairs: list[tuple[str, str]]) -> list[dict]:
        payload = {"as_of_ts": as_of_ts, "pairs": pairs}
        if self.client is None:
            with httpx.Client() as client:
                resp = client.post(f"{self.endpoint}/fx", json=payload, timeout=10)
        else:
            resp = self.client.post(f"{self.endpoint}/fx", json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data["rows"]
