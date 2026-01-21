from time import sleep


def run_scheduler_once(enqueuer, now_ts: str) -> int:
    return enqueuer.enqueue_due(now_ts)


def run_worker_once(worker, data_type: str) -> int:
    return worker.run_once(data_type)


def run_scheduler_loop(enqueuer, interval_seconds: int) -> None:
    while True:
        enqueuer.enqueue_due(now_ts=_utc_now_iso())
        sleep(interval_seconds)


def run_worker_loop(worker, data_type: str, interval_seconds: int) -> None:
    while True:
        worker.run_once(data_type)
        sleep(interval_seconds)


def _utc_now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(tz=timezone.utc).isoformat()
