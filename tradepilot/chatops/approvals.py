from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Optional, Set

from sqlalchemy.orm import Session

from tradepilot.db.models.tradeflow import SlackApprover


@dataclass
class ApproverDecision:
    allowed: bool
    approver_id: Optional[str]
    effective_from: Optional[str]
    effective_to: Optional[str]
    reason: str


class ApproverAuthorizer:
    def __init__(self, session_factory: Callable[[], Session], env_allowlist: Set[str]) -> None:
        self.session_factory = session_factory
        self.env_allowlist = env_allowlist

    def authorize(self, tenant_id: str, slack_user_id: str) -> ApproverDecision:
        try:
            with self.session_factory() as session:
                approver = (
                    session.query(SlackApprover)
                    .filter_by(tenant_id=tenant_id, slack_user_id=slack_user_id)
                    .order_by(SlackApprover.effective_from.desc())
                    .first()
                )
                if approver and _is_effective(approver.effective_from, approver.effective_to):
                    return ApproverDecision(
                        True,
                        approver.id,
                        approver.effective_from,
                        approver.effective_to,
                        "db_allowlist",
                    )
                return ApproverDecision(False, None, None, None, "not_allowed")
        except Exception:
            if slack_user_id in self.env_allowlist:
                return ApproverDecision(True, None, None, None, "bootstrap_allowlist_used")
            return ApproverDecision(False, None, None, None, "db_unavailable")


def _is_effective(effective_from: str, effective_to: Optional[str]) -> bool:
    now = datetime.now(tz=timezone.utc)
    start = _parse_timestamp(effective_from)
    if start > now:
        return False
    if effective_to is None:
        return True
    end = _parse_timestamp(effective_to)
    return end >= now


def _parse_timestamp(timestamp: str) -> datetime:
    if timestamp.endswith("Z"):
        timestamp = timestamp[:-1] + "+00:00"
    parsed = datetime.fromisoformat(timestamp)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
