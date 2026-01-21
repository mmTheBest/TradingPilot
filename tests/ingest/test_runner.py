from tradepilot.ingest.runner import run_scheduler_once


def test_run_scheduler_once_returns_int(monkeypatch):
    class DummyEnqueuer:
        def enqueue_due(self, now_ts: str) -> int:
            return 3

    assert run_scheduler_once(DummyEnqueuer(), now_ts="2026-01-20T10:00:00Z") == 3
