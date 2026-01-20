from tradepilot.chatops.slack_commands import parse_slack_command


def test_parse_slack_command_extracts_fields():
    body = (
        "command=%2Ftradepilot&text=approve%20123&user_id=U1"
        "&response_url=https%3A%2F%2Fexample.com&channel_id=C1"
    )
    cmd = parse_slack_command(body)
    assert cmd.command == "/tradepilot"
    assert cmd.subcommand == "approve"
    assert cmd.trade_id == "123"
    assert cmd.user_id == "U1"
