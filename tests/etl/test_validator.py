import pandas as pd

from src.etl.validator import DataValidator


def test_valid_dataframe_has_no_errors():

    df = pd.DataFrame({
        "company_id": ["TCS", "INFY"],
        "year": [2024, 2024],
        "sales": [100, 200]
    })

    validator = DataValidator()

    validator.validate_empty(
        df,
        "profitandloss"
    )

    validator.validate_columns(
        df,
        ["company_id", "year", "sales"]
    )

    validator.validate_duplicate_keys(
        df,
        ["company_id", "year"]
    )

    validator.validate_positive(
        df,
        "sales"
    )

    validator.validate_nulls(df)

    assert validator.errors == []


def test_empty_dataframe():

    df = pd.DataFrame()

    validator = DataValidator()

    validator.validate_empty(
        df,
        "companies"
    )

    assert len(validator.errors) == 1

    assert (
        "companies: Dataset is empty"
        in validator.errors
    )


def test_missing_columns():

    df = pd.DataFrame({
        "company_id": ["TCS"]
    })

    validator = DataValidator()

    validator.validate_columns(
        df,
        ["company_id", "year", "sales"]
    )

    assert len(validator.errors) == 1

    assert "year" in validator.errors[0]
    assert "sales" in validator.errors[0]


def test_duplicate_keys():

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

    validator.validate_duplicate_keys(
        df,
        ["company_id", "year"]
    )

    assert len(validator.errors) == 1

    assert (
        "Duplicate Key Records"
        in validator.errors[0]
    )


def test_invalid_positive_values():

    df = pd.DataFrame({
        "sales": [
            100,
            0,
            -50
        ]
    })

    validator = DataValidator()

    validator.validate_positive(
        df,
        "sales"
    )

    assert len(validator.errors) == 1

    assert (
        "sales has 2 invalid values"
        in validator.errors
    )


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

    assert (
        "company_id contains 1 NULL values"
        in validator.errors
    )