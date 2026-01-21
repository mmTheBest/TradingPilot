from tradepilot.compliance.restricted import is_restricted


def test_is_restricted():
    assert is_restricted("AAPL", {"AAPL"}) is True
