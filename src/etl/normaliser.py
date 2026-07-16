"""
src/etl/normaliser.py

Utility functions for cleaning and normalising raw data.
"""

from typing import Optional


def normalize_year(value) -> Optional[int]:
    """
    Convert different year formats into an integer year.

    Examples:
        2024 -> 2024
        "2024" -> 2024
        "FY2024" -> 2024
        "2024.0" -> 2024

    Returns:
        int or None
    """
    if value is None:
        return None

    text = str(value).strip().upper()

    text = text.replace("FY", "")

    try:
        return int(float(text))
    except ValueError:
        return None


def normalize_ticker(value: str) -> Optional[str]:
    """
    Normalize stock ticker symbols.

    Examples:
        " tcs " -> "TCS"
        "infy.ns" -> "INFY"
        "RELIANCE.NS" -> "RELIANCE"
    """
    if value is None:
        return None

    ticker = str(value).strip().upper()

    if ticker.endswith(".NS"):
        ticker = ticker[:-3]

    return ticker


if __name__ == "__main__":
    print(normalize_year("FY2024"))
    print(normalize_ticker(" tcs.ns "))