from typing import Optional

import httpx


class ReferenceApiAdapter:
    def __init__(self, endpoint: str, client: Optional[httpx.Client] = None):
        self.endpoint = endpoint
        self.client = client or httpx.Client(timeout=5.0)

    def fetch_reference(self) -> list[dict]:
        response = self.client.get(self.endpoint)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            raise ValueError("reference data must be a list")
        return data
