"""
tests/dashboard/test_app.py

N100 Financial Intelligence Platform
Sprint 4 - Day 19
Interactive Dashboard Tests
"""

import pandas as pd

from src.reports.company_report import CompanyReportGenerator


# =========================================================
# Data Loading
# =========================================================

def test_dashboard_data_loads():
    generator = CompanyReportGenerator()

    df = generator.generate(
        financial_year="Mar 2024",
        market_year="2024",
    )

    assert not df.empty
    assert len(df) == 92


# =========================================================
# Dashboard Required Columns
# =========================================================

def test_dashboard_required_columns():
    generator = CompanyReportGenerator()

    df = generator.generate()

    required = [
        "company_id",
        "company_name",
        "broad_sector",
        "sub_sector",
        "market_cap_crore",
        "pe_ratio",
        "pb_ratio",
        "return_on_equity_pct",
        "debt_to_equity",
        "operating_profit_margin_pct",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "free_cash_flow_cr",
        "composite_quality_score",
    ]

    for column in required:
        assert column in df.columns


# =========================================================
# Quality Labels
# =========================================================

def test_dashboard_quality_labels():
    generator = CompanyReportGenerator()

    df = generator.generate()
    df = generator.add_quality_labels(df)

    assert "quality_label" in df.columns

    allowed = {
        "High Quality",
        "Moderate Quality",
        "Watchlist",
        "Unknown",
    }

    assert set(df["quality_label"].unique()).issubset(
        allowed
    )


# =========================================================
# Sector Filtering
# =========================================================

def test_sector_filter():
    generator = CompanyReportGenerator()

    df = generator.generate()

    financials = df[
        df["broad_sector"] == "Financials"
    ]

    assert not financials.empty

    assert (
        financials["broad_sector"] == "Financials"
    ).all()


# =========================================================
# Company Filtering
# =========================================================

def test_company_filter():
    generator = CompanyReportGenerator()

    df = generator.generate()

    result = df[
        df["company_name"] == "ICICI Bank Ltd"
    ]

    assert len(result) == 1

    assert (
        result.iloc[0]["company_id"]
        == "ICICIBANK"
    )


# =========================================================
# Quality Filtering
# =========================================================

def test_high_quality_filter():
    generator = CompanyReportGenerator()

    df = generator.add_quality_labels(
        generator.generate()
    )

    result = df[
        df["quality_label"] == "High Quality"
    ]

    assert not result.empty

    assert (
        result["composite_quality_score"] >= 40
    ).all()


# =========================================================
# Ranking
# =========================================================

def test_quality_ranking():
    generator = CompanyReportGenerator()

    df = generator.generate()

    ranked = df.sort_values(
        "composite_quality_score",
        ascending=False,
        na_position="last",
    )

    scores = (
        ranked["composite_quality_score"]
        .dropna()
        .tolist()
    )

    assert scores == sorted(
        scores,
        reverse=True,
    )


def test_ranking_numbers():
    generator = CompanyReportGenerator()

    df = generator.generate()

    ranked = df.sort_values(
        "composite_quality_score",
        ascending=False,
        na_position="last",
    ).reset_index(drop=True)

    ranked.insert(
        0,
        "rank",
        range(1, len(ranked) + 1),
    )

    assert ranked.iloc[0]["rank"] == 1
    assert ranked.iloc[-1]["rank"] == len(ranked)


# =========================================================
# Growth Data
# =========================================================

def test_growth_metrics_available():
    generator = CompanyReportGenerator()

    df = generator.generate()

    growth_columns = [
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
    ]

    for column in growth_columns:
        assert df[column].notna().sum() > 0


# =========================================================
# Cash Flow
# =========================================================

def test_cash_flow_metrics_available():
    generator = CompanyReportGenerator()

    df = generator.generate()

    assert (
        df["cash_from_operations_cr"]
        .notna()
        .sum()
        > 0
    )

    assert (
        df["free_cash_flow_cr"]
        .notna()
        .sum()
        > 0
    )


# =========================================================
# Valuation
# =========================================================

def test_valuation_metrics_available():
    generator = CompanyReportGenerator()

    df = generator.generate()

    assert df["pe_ratio"].notna().sum() > 0
    assert df["pb_ratio"].notna().sum() > 0


# =========================================================
# CSV Export Compatibility
# =========================================================

def test_dashboard_csv_export_data():
    generator = CompanyReportGenerator()

    df = generator.add_quality_labels(
        generator.generate()
    )

    csv_data = df.to_csv(index=False)

    assert isinstance(csv_data, str)
    assert len(csv_data) > 0
    assert "company_name" in csv_data


# =========================================================
# DataFrame Integrity
# =========================================================

def test_no_duplicate_company_ids():
    generator = CompanyReportGenerator()

    df = generator.generate()

    assert not df["company_id"].duplicated().any()


def test_company_names_not_null():
    generator = CompanyReportGenerator()

    df = generator.generate()

    assert df["company_name"].notna().all()


# =========================================================
# End-to-End Dashboard Data
# =========================================================

def test_dashboard_end_to_end():
    generator = CompanyReportGenerator()

    df = generator.generate(
        financial_year="Mar 2024",
        market_year="2024",
    )

    df = generator.add_quality_labels(df)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 92
    assert "quality_label" in df.columns
    assert "composite_quality_score" in df.columns