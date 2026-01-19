from tradepilot.chatops.slack import verify_slack_signature


def test_verify_slack_signature_matches():
    secret = "secret"
    timestamp = "123"
    body = "payload"
    signature = "v0=694f6a315184e94a029178fce16d5daf385e72b43e22583fda6ba1ef2909458e"
    assert verify_slack_signature(secret, timestamp, body, signature)
