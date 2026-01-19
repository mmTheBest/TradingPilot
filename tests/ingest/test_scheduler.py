from tradepilot.ingest.scheduler import should_refresh


def test_should_refresh_when_stale():
    assert should_refresh(
        last_sync_ts="2026-01-19T10:00:00Z",
        now_ts="2026-01-19T10:06:00Z",
        sla_minutes=5,
    )
