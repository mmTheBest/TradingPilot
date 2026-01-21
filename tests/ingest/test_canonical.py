from tradepilot.ingest.canonical import canonical_json, hash_payload


def test_canonical_hash_is_stable():
    a = {"b": 2, "a": 1}
    b = {"a": 1, "b": 2}
    assert canonical_json(a) == canonical_json(b)
    assert hash_payload(a) == hash_payload(b)
