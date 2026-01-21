import hashlib
import json


def canonical_json(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def hash_payload(obj: object) -> str:
    payload = canonical_json(obj).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
