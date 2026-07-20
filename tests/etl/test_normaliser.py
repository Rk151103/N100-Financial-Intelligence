from src.etl.normaliser import normalize_year, normalize_ticker


def test_normalize_year_integer():
    assert normalize_year(2024) == 2024


def test_normalize_year_string():
    assert normalize_year("2024") == 2024


def test_normalize_year_fy_format():
    assert normalize_year("FY2024") == 2024


def test_normalize_year_invalid():
    assert normalize_year("invalid") is None


def test_normalize_ticker():
    assert normalize_ticker(" tcs ") == "TCS"


def test_normalize_ticker_ns():
    assert normalize_ticker("infy.ns") == "INFY"


def test_normalize_ticker_none():
    assert normalize_ticker(None) is None