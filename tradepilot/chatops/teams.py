import hmac
from typing import Optional


def verify_teams_shared_secret(shared_secret: str, provided: Optional[str]) -> bool:
    if not provided:
        return False
    return hmac.compare_digest(shared_secret, provided)
