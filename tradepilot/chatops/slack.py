import hashlib
import hmac


def verify_slack_signature(secret: str, timestamp: str, body: str, signature: str) -> bool:
    basestring = f"v0:{timestamp}:{body}".encode("utf-8")
    expected = "v0=" + hmac.new(secret.encode("utf-8"), basestring, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
