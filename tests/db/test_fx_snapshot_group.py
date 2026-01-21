from tradepilot.db.models.fx import FxRateSnapshot


def test_fx_snapshot_has_group_id():
    assert hasattr(FxRateSnapshot, "snapshot_id")
