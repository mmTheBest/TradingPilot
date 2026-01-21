from typing import Protocol


class PositionsAdapter(Protocol):
    def fetch_positions(self, tenant_id: str, book_id: str) -> tuple[str, list[dict]]:
        raise NotImplementedError


class LimitsAdapter(Protocol):
    def fetch_limits_version(self, tenant_id: str, book_id: str) -> tuple[str, str, list[dict]]:
        raise NotImplementedError


class FxAdapter(Protocol):
    def fetch_fx_snapshot(self, as_of_ts: str, pairs: list[tuple[str, str]]) -> list[dict]:
        raise NotImplementedError
