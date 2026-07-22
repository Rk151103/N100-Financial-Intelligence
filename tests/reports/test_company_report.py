"""
tests/reports/test_company_report.py

N100 Financial Intelligence Platform
Sprint 4 - Day 18
Company Intelligence Report Tests
"""

from pathlib import Path

import pandas as pd
import pytest

from src.reports.company_report import CompanyReportGenerator


@pytest.fixture
def generator():
    return CompanyReportGenerator()


# =========================================================
# Database / Report Loading
# =========================================================

def test_generate_all_companies(generator):
    df = generator.generate()

    assert not df.empty
    assert len(df) == 92


def test_required_columns(generator):
    df = generator.generate()

    required_columns = [
        "company_id",
        "company_name",
        "broad_sector",
        "market_cap_crore",
        "pe_ratio",
        "pb_ratio",
        "return_on_equity_pct",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "composite_quality_score",
    ]

    for column in required_columns:
        assert column in df.columns


# =========================================================
# Company Filtering
# =========================================================

def test_generate_single_company(generator):
    df = generator.generate(
        company_id="ICICIBANK"
    )

    assert len(df) == 1
    assert df.iloc[0]["company_id"] == "ICICIBANK"


def test_generate_by_name(generator):
    df = generator.generate_by_name(
        "ICICI Bank Ltd"
    )

    assert len(df) == 1
    assert df.iloc[0]["company_name"] == "ICICI Bank Ltd"


def test_generate_by_name_case_insensitive(generator):
    df = generator.generate_by_name(
        "icici bank ltd"
    )

    assert len(df) == 1
    assert df.iloc[0]["company_id"] == "ICICIBANK"


def test_invalid_company_name(generator):
    with pytest.raises(ValueError):
        generator.generate_by_name(
            "Invalid Company XYZ"
        )


# =========================================================
# Financial Data Validation
# =========================================================

def test_financial_year_join(generator):
    df = generator.generate(
        financial_year="Mar 2024",
        market_year="2024",
    )

    assert not df.empty

    populated = (
        df["composite_quality_score"]
        .notna()
        .sum()
    )

    assert populated > 0


def test_market_cap_join(generator):
    df = generator.generate(
        market_year="2024"
    )

    populated = (
        df["market_cap_crore"]
        .notna()
        .sum()
    )

    assert populated > 0


def test_quality_score_sorted_descending(generator):
    df = generator.generate()

    scores = (
        df["composite_quality_score"]
        .dropna()
        .tolist()
    )

    assert scores == sorted(
        scores,
        reverse=True
    )


# =========================================================
# Quality Labels
# =========================================================

def test_high_quality_label():
    result = CompanyReportGenerator.quality_label(
        50
    )

    assert result == "High Quality"


def test_moderate_quality_label():
    result = CompanyReportGenerator.quality_label(
        30
    )

    assert result == "Moderate Quality"


def test_watchlist_quality_label():
    result = CompanyReportGenerator.quality_label(
        10
    )

    assert result == "Watchlist"


def test_unknown_quality_label():
    result = CompanyReportGenerator.quality_label(
        None
    )

    assert result == "Unknown"


def test_add_quality_labels(generator):
    df = generator.generate()

    result = generator.add_quality_labels(df)

    assert "quality_label" in result.columns
    assert result["quality_label"].notna().all()


# =========================================================
# CSV Export
# =========================================================

def test_export_csv(generator, tmp_path):
    output = tmp_path / "company_report.csv"

    result = generator.export_csv(
        output_path=output
    )

    assert Path(result).exists()

    exported = pd.read_csv(result)

    assert not exported.empty
    assert len(exported) == 92


def test_export_single_company(generator, tmp_path):
    output = tmp_path / "icici_report.csv"

    generator.export_csv(
        output_path=output,
        company_id="ICICIBANK",
    )

    exported = pd.read_csv(output)

    assert len(exported) == 1
    assert exported.iloc[0]["company_id"] == "ICICIBANK"