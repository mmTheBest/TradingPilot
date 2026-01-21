from tradepilot.config import Settings
from tradepilot.ingest.adapters.fixtures import FixtureFxAdapter, FixtureLimitsAdapter
from tradepilot.ingest.adapters.fx_api import FxApiAdapter
from tradepilot.ingest.adapters.limits_api import LimitsApiAdapter


def build_limits_adapter(settings: Settings):
    if settings.limits_adapter_kind == "api":
        return LimitsApiAdapter(endpoint=settings.limits_api_endpoint)
    return FixtureLimitsAdapter(as_of_ts="", version_id="", rows=[])


def build_fx_adapter(settings: Settings):
    if settings.fx_adapter_kind == "api":
        return FxApiAdapter(endpoint=settings.fx_api_endpoint)
    return FixtureFxAdapter(rows=[])
