from fastapi import APIRouter, Request

from tradepilot.chatops.slack import verify_slack_signature
from tradepilot.chatops.teams import verify_teams_shared_secret
from tradepilot.config import settings

router = APIRouter()


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
