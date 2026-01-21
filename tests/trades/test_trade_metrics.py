from tradepilot.metrics import TRADE_STAGE_SUCCESS


def test_trade_stage_metrics_increment():
    before = TRADE_STAGE_SUCCESS._value.get()
    TRADE_STAGE_SUCCESS.inc()
    assert TRADE_STAGE_SUCCESS._value.get() == before + 1
