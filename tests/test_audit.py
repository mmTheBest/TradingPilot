from tradepilot.audit.models import AuditEvent, hash_payload


def test_hash_payload_is_stable():
    payload = {"a": 1}
    assert hash_payload(payload) == hash_payload(payload)


def test_audit_event_has_hashes():
    event = AuditEvent(event_type="trade.staged", actor_id="user-1", payload={"a": 1})
    assert event.input_hash
