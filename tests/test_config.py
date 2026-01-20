from tradepilot.config import Settings


def test_settings_env_override(monkeypatch):
    monkeypatch.setenv("TRADEPILOT_EMSX_ENDPOINT", "https://emsx.test")
    settings = Settings()
    assert settings.emsx_endpoint == "https://emsx.test"


def test_settings_allows_slack_approver_allowlist(monkeypatch):
    monkeypatch.setenv("TRADEPILOT_SLACK_APPROVER_ALLOWLIST", "U1,U2")
    settings = Settings()
    assert settings.slack_approver_allowlist == "U1,U2"
