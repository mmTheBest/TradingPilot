from prometheus_client import Counter, Gauge, generate_latest

INGEST_SUCCESS = Counter("tradepilot_ingest_success_total", "ingest successes", ["data_type"])
INGEST_FAILURE = Counter("tradepilot_ingest_failure_total", "ingest failures", ["data_type"])
QUEUE_DEPTH = Gauge("tradepilot_ingest_queue_depth", "ingest queue depth", ["data_type"])


def metrics_payload() -> bytes:
    return generate_latest()
