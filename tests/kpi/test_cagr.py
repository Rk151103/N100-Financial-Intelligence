from src.analytics.cagr import calculate_cagr


def test_cagr_calculation():
    assert calculate_cagr(100, 200, 5) == 14.87


def test_cagr_no_growth():
    assert calculate_cagr(100, 100, 5) == 0.0


def test_cagr_invalid_beginning_value():
    assert calculate_cagr(0, 200, 5) is None


def test_cagr_invalid_years():
    assert calculate_cagr(100, 200, 0) is None


def test_cagr_none_value():
    assert calculate_cagr(None, 200, 5) is None