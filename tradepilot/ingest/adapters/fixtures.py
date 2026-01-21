from dataclasses import dataclass

from tradepilot.ingest.adapters.base import FxAdapter, LimitsAdapter, PositionsAdapter


@dataclass
class FixturePositionsAdapter(PositionsAdapter):
    as_of_ts: str
    rows: list[dict]

    def fetch_positions(self, tenant_id: str, book_id: str) -> tuple[str, list[dict]]:
        return self.as_of_ts, list(self.rows)


@dataclass
class FixtureLimitsAdapter(LimitsAdapter):
    as_of_ts: str
    version_id: str
    rows: list[dict]

    def fetch_limits_version(self, tenant_id: str, book_id: str) -> tuple[str, str, list[dict]]:
        return self.as_of_ts, self.version_id, list(self.rows)


@dataclass
class FixtureFxAdapter(FxAdapter):
    rows: list[dict]

    def fetch_fx_snapshot(self, as_of_ts: str, pairs: list[tuple[str, str]]) -> list[dict]:
        return list(self.rows)
