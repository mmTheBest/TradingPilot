import hmac
import hashlib
from datetime import datetime, timezone
from urllib.parse import urlencode

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from tradepilot.api import chatops as chatops_api
from tradepilot.chatops.approvals import ApproverAuthorizer
from tradepilot.config import settings
from tradepilot.db.base import Base
from tradepilot.db.models.tradeflow import SlackApprover, StagedTradeRecord, TradeApproval, TradeSubmitQueue
from tradepilot.main import app
from tradepilot.trades.repository import TradeRepository


def sign_slack_body(secret: str, timestamp: str, body: str) -> str:
    basestring = f"v0:{timestamp}:{body}".encode("utf-8")
    digest = hmac.new(secret.encode("utf-8"), basestring, hashlib.sha256).hexdigest()
    return f"v0={digest}"


def test_slash_command_approve_updates_trade_and_enqueues(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    repo = TradeRepository(session_factory=SessionLocal)
    now = datetime.now(tz=timezone.utc).isoformat()
    trade_id = repo.create_staged_trade(
        tenant_id="tenant-1",
        book_id="book-1",
        symbol="AAPL",
        side="buy",
        quantity=10,
        order_type="market",
        limit_price=None,
        status="staged",
        emsx_order_id="emsx-1",
        positions_as_of_ts=now,
        limits_version_id="limits-1",
        fx_rate_snapshot_id="fx-1",
    )

    with SessionLocal() as session:
        session.add(
            SlackApprover(
                id="approver-1",
                tenant_id="tenant-1",
                slack_user_id="U1",
                role="APPROVER",
                effective_from=now,
                effective_to=None,
                added_by="admin",
                added_at=now,
            )
        )
        session.commit()

    authorizer = ApproverAuthorizer(session_factory=SessionLocal, env_allowlist=set())
    app.dependency_overrides[chatops_api.get_trade_repository] = lambda: repo
    app.dependency_overrides[chatops_api.get_approver_authorizer] = lambda: authorizer
    monkeypatch.setattr(chatops_api, "post_in_channel", lambda *_args, **_kwargs: None)
    settings.slack_signing_secret = "secret"

    payload = {
        "command": "/tradepilot",
        "text": f"approve {trade_id} looks good",
        "user_id": "U1",
        "response_url": "https://example.com/response",
        "channel_id": "C1",
    }
    body = urlencode(payload)
    timestamp = "123"
    signature = sign_slack_body(settings.slack_signing_secret, timestamp, body)

    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/chatops/slack/commands",
            data=body,
            headers={
                "content-type": "application/x-www-form-urlencoded",
                "x-slack-request-timestamp": timestamp,
                "x-slack-signature": signature,
            },
        )
        assert response.status_code == 200
        assert response.json()["response_type"] == "ephemeral"
    finally:
        app.dependency_overrides.clear()

    with SessionLocal() as session:
        trade = session.get(StagedTradeRecord, trade_id)
        assert trade.status == "approved"
        assert session.query(TradeApproval).count() == 1
        assert session.query(TradeSubmitQueue).count() == 1
