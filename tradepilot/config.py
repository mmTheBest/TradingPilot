from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TRADEPILOT_", env_file=".env", extra="ignore")
    database_url: str = "postgresql+psycopg://tradepilot:tradepilot@localhost:5432/tradepilot"
    positions_view: str = "positions_view"
    slack_signing_secret: str = "change-me"
    slack_bot_token: str = "change-me"
    slack_approver_allowlist: str = ""
    teams_app_id: str = "change-me"
    teams_app_password: str = "change-me"
    emsx_endpoint: str = "http://localhost:9000"
    audit_bucket: str = "tradepilot-audit"
    ingest_poke_secret: str = "change-me"


settings = Settings()
