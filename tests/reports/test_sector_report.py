"""
tests/reports/test_sector_report.py

N100 Financial Intelligence Platform
Sprint 4 - Day 20
Sector Intelligence Engine Tests
"""

from pathlib import Path

import pandas as pd
import pytest

from src.reports.sector_report import SectorReportGenerator


@pytest.fixture
def generator():
    return SectorReportGenerator()


# =========================================================
# Company Data Loading
# =========================================================

def test_load_company_data(generator):
    df = generator.load_company_data()

    assert not df.empty
    assert len(df) == 92


def test_company_data_required_columns(generator):
    df = generator.load_company_data()

    required = [
        "company_id",
        "company_name",
        "broad_sector",
        "market_cap_crore",
        "return_on_equity_pct",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "composite_quality_score",
    ]

    for column in required:
        assert column in df.columns


# =========================================================
# Sector Summary
# =========================================================

def test_generate_sector_report(generator):
    report = generator.generate()

    assert not report.empty
    assert len(report) == 10


def test_sector_company_total(generator):
    report = generator.generate()

    assert report["company_count"].sum() == 92


def test_unique_sectors(generator):
    report = generator.generate()

    assert report["broad_sector"].nunique() == 10


def test_sector_report_columns(generator):
    report = generator.generate()

    required = [
        "sector_rank",
        "broad_sector",
        "company_count",
        "total_market_cap_crore",
        "average_roe_pct",
        "average_debt_to_equity",
        "average_revenue_cagr_5yr",
        "average_pat_cagr_5yr",
        "average_quality_score",
    ]

    for column in required:
        assert column in report.columns


# =========================================================
# Ranking
# =========================================================

def test_sector_rank_starts_at_one(generator):
    report = generator.generate()

    assert report.iloc[0]["sector_rank"] == 1


def test_sector_rank_sequence(generator):
    report = generator.generate()

    assert report["sector_rank"].tolist() == list(
        range(1, len(report) + 1)
    )


def test_quality_score_sorted(generator):
    report = generator.generate()

    scores = (
        report["average_quality_score"]
        .dropna()
        .tolist()
    )

    assert scores == sorted(
        scores,
        reverse=True,
    )


# =========================================================
# Financial Sector
# =========================================================

def test_financial_sector(generator):
    df = generator.get_sector("Financials")

    assert not df.empty
    assert len(df) == 23

    assert (
        df["broad_sector"] == "Financials"
    ).all()


def test_sector_case_insensitive(generator):
    df = generator.get_sector("financials")

    assert len(df) == 23


def test_invalid_sector(generator):
    with pytest.raises(ValueError):
        generator.get_sector(
            "Invalid Sector XYZ"
        )


# =========================================================
# Sector Leaders
# =========================================================

def test_sector_leaders(generator):
    leaders = generator.sector_leaders(
        "Financials",
        limit=5,
    )

    assert len(leaders) == 5

    assert (
        leaders["broad_sector"] == "Financials"
    ).all()


def test_sector_leaders_sorted(generator):
    leaders = generator.sector_leaders(
        "Financials",
        limit=5,
    )

    scores = (
        leaders["composite_quality_score"]
        .dropna()
        .tolist()
    )

    assert scores == sorted(
        scores,
        reverse=True,
    )


# =========================================================
# Aggregation Validation
# =========================================================

def test_financial_company_count(generator):
    report = generator.generate()

    financials = report[
        report["broad_sector"] == "Financials"
    ]

    assert len(financials) == 1
    assert financials.iloc[0]["company_count"] == 23


def test_real_estate_company_count(generator):
    report = generator.generate()

    real_estate = report[
        report["broad_sector"] == "Real Estate"
    ]

    assert len(real_estate) == 1
    assert real_estate.iloc[0]["company_count"] == 2


# =========================================================
# Market Cap
# =========================================================

def test_market_cap_aggregation(generator):
    report = generator.generate()

    assert (
        report["total_market_cap_crore"] >= 0
    ).all()


# =========================================================
# CSV Export
# =========================================================

def test_export_csv(generator, tmp_path):
    output = (
        tmp_path /
        "sector_intelligence_report.csv"
    )

    result = generator.export_csv(
        output_path=output
    )

    assert Path(result).exists()

    exported = pd.read_csv(result)

    assert len(exported) == 10
    assert "broad_sector" in exported.columns


# =========================================================
# End-to-End
# =========================================================

def test_sector_report_end_to_end(generator):
    report = generator.generate()

    leaders = generator.sector_leaders(
        "Financials",
        limit=5,
    )

    assert isinstance(report, pd.DataFrame)
    assert isinstance(leaders, pd.DataFrame)

    assert len(report) == 10
    assert report["company_count"].sum() == 92
    assert len(leaders) == 5