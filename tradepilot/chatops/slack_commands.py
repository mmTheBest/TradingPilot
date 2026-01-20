from dataclasses import dataclass
from urllib.parse import parse_qs


@dataclass
class SlackCommand:
    command: str
    subcommand: str
    trade_id: str
    reason: str
    user_id: str
    response_url: str
    channel_id: str


def parse_slack_command(body: str) -> SlackCommand:
    data = {key: value[0] for key, value in parse_qs(body).items()}
    text = data.get("text", "")
    parts = text.split(" ", 2)
    subcommand = parts[0] if len(parts) > 0 else ""
    trade_id = parts[1] if len(parts) > 1 else ""
    reason = parts[2] if len(parts) > 2 else ""
    return SlackCommand(
        command=data.get("command", ""),
        subcommand=subcommand,
        trade_id=trade_id,
        reason=reason,
        user_id=data.get("user_id", ""),
        response_url=data.get("response_url", ""),
        channel_id=data.get("channel_id", ""),
    )
