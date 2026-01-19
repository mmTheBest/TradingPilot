from tradepilot.config import Settings


def test_settings_env_override(monkeypatch):
    monkeypatch.setenv("TRADEPILOT_EMSX_ENDPOINT", "https://emsx.test")
    settings = Settings()
    assert settings.emsx_endpoint == "https://emsx.test"
