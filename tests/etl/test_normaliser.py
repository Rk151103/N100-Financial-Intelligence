"""
tests/etl/test_normaliser.py

Unit tests for ETL normalisation functions.
"""

from src.etl.normaliser import normalize_year, normalize_ticker


# =========================================================
# normalize_year Tests
# =========================================================

def test_normalize_year_integer():
    assert normalize_year(2024) == 2024


def test_normalize_year_string():
    assert normalize_year("2024") == 2024


def test_normalize_year_fy_format():
    assert normalize_year("FY2024") == 2024


def test_normalize_year_invalid():
    assert normalize_year("invalid") is None


def test_normalize_year_float_string():
    assert normalize_year("2024.0") == 2024


def test_normalize_year_with_spaces():
    assert normalize_year(" 2024 ") == 2024


def test_normalize_year_lowercase_fy():
    assert normalize_year("fy2024") == 2024


def test_normalize_year_none():
    assert normalize_year(None) is None


def test_normalize_year_empty_string():
    assert normalize_year("") is None


# =========================================================
# normalize_ticker Tests
# =========================================================

def test_normalize_ticker():
    assert normalize_ticker(" tcs ") == "TCS"


def test_normalize_ticker_ns():
    assert normalize_ticker("infy.ns") == "INFY"


def test_normalize_ticker_none():
    assert normalize_ticker(None) is None


def test_normalize_ticker_lowercase():
    assert normalize_ticker("tcs") == "TCS"


def test_normalize_ticker_with_spaces():
    assert normalize_ticker("  INFY  ") == "INFY"


def test_normalize_ticker_ns_uppercase():
    assert normalize_ticker("TCS.NS") == "TCS"


def test_normalize_ticker_ns_lowercase():
    assert normalize_ticker("reliance.ns") == "RELIANCE"


def test_normalize_ticker_empty_string():
    assert normalize_ticker("") == ""