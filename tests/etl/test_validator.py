"""
tests/etl/test_validator.py

Unit tests for DataValidator.
N100 Financial Intelligence Platform
Sprint 1 - Data Quality Rules
"""

import pandas as pd

from src.etl.validator import DataValidator


# =========================================================
# Existing Basic Validator Tests
# =========================================================

def test_valid_dataframe_has_no_errors():
    df = pd.DataFrame({
        "company_id": ["TCS", "INFY"],
        "year": [2024, 2024],
        "sales": [100, 200]
    })

    validator = DataValidator()

    validator.validate_empty(df, "profitandloss")
    validator.validate_columns(
        df,
        ["company_id", "year", "sales"]
    )
    validator.validate_duplicate_keys(
        df,
        ["company_id", "year"]
    )
    validator.validate_positive(df, "sales")

    assert validator.errors == []


def test_empty_dataframe():
    df = pd.DataFrame()

    validator = DataValidator()

    validator.validate_empty(
        df,
        "profitandloss"
    )

    assert len(validator.errors) == 1


def test_missing_columns():
    df = pd.DataFrame({
        "company_id": ["TCS"]
    })

    validator = DataValidator()

    validator.validate_columns(
        df,
        ["company_id", "year"]
    )

    assert len(validator.errors) == 1


def test_duplicate_keys():
    df = pd.DataFrame({
        "company_id": ["TCS", "TCS"],
        "year": [2024, 2024]
    })

    validator = DataValidator()

    validator.validate_duplicate_keys(
        df,
        ["company_id", "year"]
    )

    assert len(validator.errors) == 1


def test_invalid_positive_values():
    df = pd.DataFrame({
        "sales": [100, -50, 0]
    })

    validator = DataValidator()

    validator.validate_positive(
        df,
        "sales"
    )

    assert len(validator.errors) == 1


def test_null_values():
    df = pd.DataFrame({
        "company_id": [
            "TCS",
            None
        ]
    })

    validator = DataValidator()

    validator.validate_nulls(df)

    assert len(validator.errors) == 1


# =========================================================
# DQ-01 — Primary Key Uniqueness
# =========================================================

def test_dq01_primary_key_unique():
    df = pd.DataFrame({
        "id": [
            "TCS",
            "TCS"
        ]
    })

    validator = DataValidator()

    validator.dq01_primary_key_unique(df)

    assert any(
        "DQ-01" in error
        for error in validator.errors
    )


# =========================================================
# DQ-02 — Company-Year Composite Key
# =========================================================

def test_dq02_company_year_unique():
    df = pd.DataFrame({
        "company_id": [
            "TCS",
            "TCS"
        ],
        "year": [
            2024,
            2024
        ]
    })

    validator = DataValidator()

    validator.dq02_company_year_unique(df)

    assert any(
        "DQ-02" in error
        for error in validator.errors
    )


# =========================================================
# DQ-03 — Foreign Key Integrity
# =========================================================

def test_dq03_foreign_key_integrity():
    df = pd.DataFrame({
        "company_id": [
            "TCS",
            "INVALID"
        ]
    })

    valid_ids = {
        "TCS",
        "INFY"
    }

    validator = DataValidator()

    validator.dq03_foreign_key_integrity(
        df,
        valid_ids
    )

    assert any(
        "DQ-03" in error
        for error in validator.errors
    )


# =========================================================
# DQ-04 — Balance Sheet Balance
# =========================================================

def test_dq04_balance_sheet_balance():
    df = pd.DataFrame({
        "total_liabilities": [
            100,
            150
        ],
        "total_assets": [
            100,
            100
        ]
    })

    validator = DataValidator()

    validator.dq04_balance_sheet_balance(df)

    assert any(
        "DQ-04" in error
        for error in validator.errors
    )


# =========================================================
# DQ-05 — OPM Cross Check
# =========================================================

def test_dq05_opm_cross_check():
    df = pd.DataFrame({
        "sales": [
            100
        ],
        "operating_profit": [
            20
        ],
        "opm_percentage": [
            10
        ]
    })

    validator = DataValidator()

    validator.dq05_opm_cross_check(df)

    assert any(
        "DQ-05" in error
        for error in validator.errors
    )


# =========================================================
# DQ-06 — Positive Sales
# =========================================================

def test_dq06_positive_sales():
    df = pd.DataFrame({
        "sales": [
            100,
            0,
            -10
        ]
    })

    validator = DataValidator()

    validator.dq06_positive_sales(df)

    assert any(
        "DQ-06" in error
        for error in validator.errors
    )


# =========================================================
# DQ-07 — Net Cash Flow Check
# =========================================================

def test_dq07_net_cash_flow():
    df = pd.DataFrame({
        "operating_activity": [
            100
        ],
        "investing_activity": [
            -20
        ],
        "financing_activity": [
            -10
        ],
        "net_cash_flow": [
            50
        ]
    })

    validator = DataValidator()

    validator.dq07_net_cash_flow(df)

    assert any(
        "DQ-07" in error
        for error in validator.errors
    )


# =========================================================
# DQ-08 — Tax Rate Range
# =========================================================

def test_dq08_tax_rate():
    df = pd.DataFrame({
        "tax_percentage": [
            25,
            120
        ]
    })

    validator = DataValidator()

    validator.dq08_tax_rate(df)

    assert any(
        "DQ-08" in error
        for error in validator.errors
    )


# =========================================================
# DQ-09 — Dividend Payout Range
# =========================================================

def test_dq09_dividend_payout():
    df = pd.DataFrame({
        "dividend_payout": [
            50,
            150
        ]
    })

    validator = DataValidator()

    validator.dq09_dividend_payout(df)

    assert any(
        "DQ-09" in error
        for error in validator.errors
    )


# =========================================================
# DQ-10 — EPS Sign Consistency
# =========================================================

def test_dq10_eps_sign():
    df = pd.DataFrame({
        "eps": [
            -10
        ],
        "net_profit": [
            100
        ]
    })

    validator = DataValidator()

    validator.dq10_eps_sign(df)

    assert any(
        "DQ-10" in error
        for error in validator.errors
    )


# =========================================================
# DQ-11 — URL Format
# =========================================================

def test_dq11_url_format():
    df = pd.DataFrame({
        "website": [
            "https://example.com",
            "invalid-url"
        ]
    })

    validator = DataValidator()

    validator.dq11_url_format(
        df,
        "website"
    )

    assert any(
        "DQ-11" in error
        for error in validator.errors
    )


# =========================================================
# DQ-12 — Year Range
# =========================================================

def test_dq12_year_range():
    df = pd.DataFrame({
        "year": [
            2024,
            1800
        ]
    })

    validator = DataValidator()

    validator.dq12_year_range(df)

    assert any(
        "DQ-12" in error
        for error in validator.errors
    )


# =========================================================
# DQ-13 — Company ID Not NULL
# =========================================================

def test_dq13_company_id_not_null():
    df = pd.DataFrame({
        "company_id": [
            "TCS",
            None
        ]
    })

    validator = DataValidator()

    validator.dq13_company_id_not_null(df)

    assert any(
        "DQ-13" in error
        for error in validator.errors
    )


# =========================================================
# DQ-14 — Total Assets Positive
# =========================================================

def test_dq14_total_assets():
    df = pd.DataFrame({
        "total_assets": [
            1000,
            -100
        ]
    })

    validator = DataValidator()

    validator.dq14_total_assets(df)

    assert any(
        "DQ-14" in error
        for error in validator.errors
    )


# =========================================================
# DQ-15 — Interest Values
# =========================================================

def test_dq15_interest_values():
    df = pd.DataFrame({
        "interest": [
            10,
            -5
        ]
    })

    validator = DataValidator()

    validator.dq15_interest_values(df)

    assert any(
        "DQ-15" in error
        for error in validator.errors
    )


# =========================================================
# DQ-16 — NSE/BSE Profile Coverage
# =========================================================

def test_dq16_market_profile_coverage():
    df = pd.DataFrame({
        "nse_profile": [
            "https://nse.example.com",
            None
        ],
        "bse_profile": [
            None,
            None
        ]
    })

    validator = DataValidator()

    validator.dq16_market_profile_coverage(df)

    assert any(
        "DQ-16" in error
        for error in validator.errors
    )


# =========================================================
# Reset Validator
# =========================================================

def test_validator_reset():
    validator = DataValidator()

    validator.errors.append(
        "Test Error"
    )

    validator.reset()

    assert validator.errors == []