from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request

from tradepilot.chatops.approvals import ApproverAuthorizer
from tradepilot.chatops.slack_commands import parse_slack_command
from tradepilot.chatops.slack import verify_slack_signature
from tradepilot.chatops.slack_notify import post_in_channel
from tradepilot.chatops.teams import verify_teams_shared_secret
from tradepilot.config import settings
from tradepilot.db.session import SessionLocal
from tradepilot.trades.repository import TradeRepository

router = APIRouter()


def get_trade_repository() -> TradeRepository:
    return TradeRepository(session_factory=SessionLocal)


def get_approver_authorizer() -> ApproverAuthorizer:
    allowlist = {item.strip() for item in settings.slack_approver_allowlist.split(",") if item.strip()}
    return ApproverAuthorizer(session_factory=SessionLocal, env_allowlist=allowlist)


@router.post("/api/v1/chatops/events")
async def ingest_chatops_event(request: Request):
    body = (await request.body()).decode("utf-8")
    platform = request.headers.get("x-chat-platform", "slack")
    if platform == "slack":
        timestamp = request.headers.get("x-slack-request-timestamp", "")
        signature = request.headers.get("x-slack-signature", "")
        if not verify_slack_signature(settings.slack_signing_secret, timestamp, body, signature):
            return {"status": "invalid_signature"}
    if platform == "teams":
        shared = request.headers.get("x-teams-shared-secret")
        if not verify_teams_shared_secret(settings.teams_app_password, shared):
            return {"status": "invalid_signature"}
    return {"status": "ok"}


@router.post("/api/v1/chatops/slack/commands")
async def slack_commands(
    request: Request,
    repository: TradeRepository = Depends(get_trade_repository),
    authorizer: ApproverAuthorizer = Depends(get_approver_authorizer),
):
    body = (await request.body()).decode("utf-8")
    timestamp = request.headers.get("x-slack-request-timestamp", "")
    signature = request.headers.get("x-slack-signature", "")
    if not verify_slack_signature(settings.slack_signing_secret, timestamp, body, signature):
        return {"response_type": "ephemeral", "text": "invalid signature"}

    command = parse_slack_command(body)
    if command.subcommand not in {"approve", "reject"}:
        return {"response_type": "ephemeral", "text": "unsupported command"}
    if not command.trade_id:
        return {"response_type": "ephemeral", "text": "missing trade_id"}

    trade = repository.get_trade(command.trade_id)
    if trade is None:
        return {"response_type": "ephemeral", "text": "trade not found"}
    if trade.status != "staged":
        return {"response_type": "ephemeral", "text": f"trade not in staged status: {trade.status}"}

    decision = authorizer.authorize(trade.tenant_id, command.user_id)
    if not decision.allowed:
        return {"response_type": "ephemeral", "text": f"not authorized: {decision.reason}"}

    now = datetime.now(tz=timezone.utc).isoformat()
    if command.subcommand == "approve":
        repository.record_approval(
            trade_id=command.trade_id,
            action="approve",
            reason=command.reason or None,
            slack_user_id=command.user_id,
            approver_id=decision.approver_id,
            approver_effective_from=decision.effective_from,
            approver_effective_to=decision.effective_to,
        )
        repository.update_trade_status(command.trade_id, "approved")
        repository.enqueue_submission(command.trade_id, next_attempt_at=now)
        post_in_channel(
            command.response_url,
            f"Trade {command.trade_id} approved by <@{command.user_id}>",
        )
        return {"response_type": "ephemeral", "text": f"approved {command.trade_id}"}

    repository.record_approval(
        trade_id=command.trade_id,
        action="reject",
        reason=command.reason or None,
        slack_user_id=command.user_id,
        approver_id=decision.approver_id,
        approver_effective_from=decision.effective_from,
        approver_effective_to=decision.effective_to,
    )
    repository.update_trade_status(command.trade_id, "rejected")
    post_in_channel(
        command.response_url,
        f"Trade {command.trade_id} rejected by <@{command.user_id}>",
    )
    return {"response_type": "ephemeral", "text": f"rejected {command.trade_id}"}
