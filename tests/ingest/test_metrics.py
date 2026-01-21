from tradepilot.metrics import INGEST_FAILURE, INGEST_SUCCESS


def test_ingest_metrics_increment():
    before_success = INGEST_SUCCESS.labels("positions")._value.get()
    before_failure = INGEST_FAILURE.labels("positions")._value.get()
    INGEST_SUCCESS.labels("positions").inc()
    INGEST_FAILURE.labels("positions").inc()
    assert INGEST_SUCCESS.labels("positions")._value.get() == before_success + 1
    assert INGEST_FAILURE.labels("positions")._value.get() == before_failure + 1
