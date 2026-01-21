from tradepilot.config import Settings
from tradepilot.ingest.adapters.factory import build_limits_adapter
from tradepilot.ingest.adapters.fixtures import FixtureLimitsAdapter


def test_factory_defaults_to_fixture(monkeypatch):
    monkeypatch.setenv("TRADEPILOT_LIMITS_ADAPTER_KIND", "fixture")
    settings = Settings()
    adapter = build_limits_adapter(settings)
    assert isinstance(adapter, FixtureLimitsAdapter)
