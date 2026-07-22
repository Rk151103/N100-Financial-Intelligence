"""
tests/screener/test_watchlist.py

N100 Financial Intelligence Platform
Sprint 3 - Day 20
Watchlist Intelligence Engine Tests
"""

from pathlib import Path

import pandas as pd
import pytest

from src.screener.watchlist import (
    WatchlistIntelligenceEngine,
)


YEAR = "Mar 2024"

WATCHLIST = [
    "TCS",
    "INFY",
    "HCLTECH",
    "LTIM",
    "RELIANCE",
    "ITC",
    "MARUTI",
    "HAL",
]


# =========================================================
# Initialization
# =========================================================

def test_engine_initialization():
    engine = WatchlistIntelligenceEngine()

    assert engine.db_path.exists()
    assert engine.company_engine is not None


# =========================================================
# Company ID Normalization
# =========================================================

def test_normalize_company_ids():
    result = (
        WatchlistIntelligenceEngine
        .normalize_company_ids(
            ["tcs", " infy ", "HAL"]
        )
    )

    assert result == [
        "TCS",
        "INFY",
        "HAL",
    ]


def test_normalize_removes_duplicates():
    result = (
        WatchlistIntelligenceEngine
        .normalize_company_ids(
            ["TCS", "tcs", "INFY", "INFY"]
        )
    )

    assert result == [
        "TCS",
        "INFY",
    ]


def test_normalize_skips_blank_values():
    result = (
        WatchlistIntelligenceEngine
        .normalize_company_ids(
            ["TCS", "", "   ", "INFY"]
        )
    )

    assert result == [
        "TCS",
        "INFY",
    ]


def test_none_watchlist_rejected():
    with pytest.raises(ValueError):
        (
            WatchlistIntelligenceEngine
            .normalize_company_ids(None)
        )


def test_empty_watchlist_rejected():
    with pytest.raises(ValueError):
        (
            WatchlistIntelligenceEngine
            .normalize_company_ids([])
        )


def test_blank_watchlist_rejected():
    with pytest.raises(ValueError):
        (
            WatchlistIntelligenceEngine
            .normalize_company_ids(
                ["", "   "]
            )
        )


# =========================================================
# Real Watchlist Analysis
# =========================================================

def test_analyse_watchlist():
    engine = WatchlistIntelligenceEngine()

    df = engine.analyse_watchlist(
        WATCHLIST,
        YEAR,
    )

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 8


def test_watchlist_required_columns():
    engine = WatchlistIntelligenceEngine()

    df = engine.analyse_watchlist(
        WATCHLIST,
        YEAR,
    )

    required = {
        "watchlist_rank",
        "company_id",
        "company_name",
        "broad_sector",
        "year",
        "overall_rank",
        "sector_rank",
        "ranking_score",
        "intelligence_score",
        "assessment",
        "quality_score",
        "growth_score",
        "profitability_score",
        "financial_strength_score",
        "efficiency_score",
        "strength_count",
        "risk_count",
    }

    assert required.issubset(
        set(df.columns)
    )


def test_watchlist_sorted_descending():
    engine = WatchlistIntelligenceEngine()

    df = engine.analyse_watchlist(
        WATCHLIST,
        YEAR,
    )

    scores = (
        df["intelligence_score"]
        .tolist()
    )

    assert scores == sorted(
        scores,
        reverse=True,
    )


def test_watchlist_rank_sequence():
    engine = WatchlistIntelligenceEngine()

    df = engine.analyse_watchlist(
        WATCHLIST,
        YEAR,
    )

    assert (
        df["watchlist_rank"].tolist()
        == list(
            range(
                1,
                len(df) + 1,
            )
        )
    )


def test_duplicate_companies_not_repeated():
    engine = WatchlistIntelligenceEngine()

    df = engine.analyse_watchlist(
        [
            "TCS",
            "tcs",
            "INFY",
            "INFY",
        ],
        YEAR,
    )

    assert len(df) == 2

    assert set(
        df["company_id"]
    ) == {
        "TCS",
        "INFY",
    }


# =========================================================
# Invalid Company Handling
# =========================================================

def test_invalid_company_raises():
    engine = WatchlistIntelligenceEngine()

    with pytest.raises(ValueError):
        engine.analyse_watchlist(
            [
                "TCS",
                "INVALID_COMPANY",
            ],
            YEAR,
        )


def test_ignore_invalid_company():
    engine = WatchlistIntelligenceEngine()

    df = engine.analyse_watchlist(
        [
            "TCS",
            "INVALID_COMPANY",
            "INFY",
        ],
        YEAR,
        ignore_invalid=True,
    )

    assert len(df) == 2

    assert (
        df.attrs["invalid_companies"]
        == ["INVALID_COMPANY"]
    )


def test_all_invalid_companies_rejected():
    engine = WatchlistIntelligenceEngine()

    with pytest.raises(ValueError):
        engine.analyse_watchlist(
            [
                "INVALID_ONE",
                "INVALID_TWO",
            ],
            YEAR,
            ignore_invalid=True,
        )


# =========================================================
# Top Companies
# =========================================================

def test_top_companies():
    engine = WatchlistIntelligenceEngine()

    result = engine.top_companies(
        WATCHLIST,
        YEAR,
        n=3,
    )

    assert len(result) == 3

    assert (
        result.iloc[0]["company_id"]
        == "HAL"
    )


def test_top_companies_invalid_n():
    engine = WatchlistIntelligenceEngine()

    with pytest.raises(ValueError):
        engine.top_companies(
            WATCHLIST,
            YEAR,
            n=0,
        )


# =========================================================
# Strongest / Weakest
# =========================================================

def test_strongest_company():
    engine = WatchlistIntelligenceEngine()

    result = engine.strongest_company(
        WATCHLIST,
        YEAR,
    )

    assert result["company_id"] == "HAL"

    assert result[
        "intelligence_score"
    ] == pytest.approx(
        89.12
    )


def test_weakest_company():
    engine = WatchlistIntelligenceEngine()

    result = engine.weakest_company(
        WATCHLIST,
        YEAR,
    )

    assert result["company_id"] == "RELIANCE"

    assert result[
        "intelligence_score"
    ] == pytest.approx(
        39.65
    )


# =========================================================
# Sector Distribution
# =========================================================

def test_sector_distribution():
    engine = WatchlistIntelligenceEngine()

    result = engine.sector_distribution(
        WATCHLIST,
        YEAR,
    )

    assert (
        result["company_count"].sum()
        == 8
    )

    assert result[
        "weight_pct"
    ].sum() == pytest.approx(
        100.0
    )


def test_information_technology_weight():
    engine = WatchlistIntelligenceEngine()

    result = engine.sector_distribution(
        WATCHLIST,
        YEAR,
    )

    it_row = result[
        result["broad_sector"]
        == "Information Technology"
    ].iloc[0]

    assert it_row[
        "company_count"
    ] == 4

    assert it_row[
        "weight_pct"
    ] == pytest.approx(
        50.0
    )


def test_sector_count():
    engine = WatchlistIntelligenceEngine()

    result = engine.sector_distribution(
        WATCHLIST,
        YEAR,
    )

    assert len(result) == 5


# =========================================================
# Assessment Distribution
# =========================================================

def test_assessment_distribution():
    engine = WatchlistIntelligenceEngine()

    result = engine.assessment_distribution(
        WATCHLIST,
        YEAR,
    )

    assert (
        result["company_count"].sum()
        == 8
    )

    assert result[
        "weight_pct"
    ].sum() == pytest.approx(
        100.0
    )


def test_good_assessment_count():
    engine = WatchlistIntelligenceEngine()

    result = engine.assessment_distribution(
        WATCHLIST,
        YEAR,
    )

    good = result[
        result["assessment"]
        == "Good"
    ].iloc[0]

    assert good["company_count"] == 4
    assert good["weight_pct"] == pytest.approx(50.0)


# =========================================================
# Summary
# =========================================================

def test_watchlist_summary():
    engine = WatchlistIntelligenceEngine()

    result = engine.summary(
        WATCHLIST,
        YEAR,
    )

    assert result["company_count"] == 8
    assert result["sector_count"] == 5

    assert result[
        "average_intelligence_score"
    ] == pytest.approx(
        67.76
    )

    assert result[
        "average_ranking_score"
    ] == pytest.approx(
        58.64
    )

    assert (
        result["strongest_company_id"]
        == "HAL"
    )

    assert (
        result["weakest_company_id"]
        == "RELIANCE"
    )

    assert (
        result["largest_sector"]
        == "Information Technology"
    )


def test_summary_assessment_counts():
    engine = WatchlistIntelligenceEngine()

    result = engine.summary(
        WATCHLIST,
        YEAR,
    )

    assert result["strong_count"] == 1
    assert result["good_count"] == 4
    assert result["average_count"] == 2
    assert result["weak_count"] == 1


def test_summary_ignore_invalid():
    engine = WatchlistIntelligenceEngine()

    result = engine.summary(
        [
            "TCS",
            "INFY",
            "INVALID_COMPANY",
        ],
        YEAR,
        ignore_invalid=True,
    )

    assert result["company_count"] == 2

    assert (
        result["invalid_companies"]
        == ["INVALID_COMPANY"]
    )


# =========================================================
# Narrative
# =========================================================

def test_generate_summary():
    engine = WatchlistIntelligenceEngine()

    summary = engine.generate_summary(
        WATCHLIST,
        YEAR,
    )

    assert "8 companies" in summary
    assert "5 sectors" in summary
    assert "67.76/100" in summary
    assert "Hindustan Aeronautics Ltd" in summary
    assert "89.12/100" in summary
    assert "Reliance Industries Ltd" in summary
    assert "39.65/100" in summary


# =========================================================
# CSV Export
# =========================================================

def test_export_csv(tmp_path):
    engine = WatchlistIntelligenceEngine()

    output_file = (
        tmp_path
        / "watchlist_test.csv"
    )

    result = engine.export_csv(
        WATCHLIST,
        YEAR,
        output_path=output_file,
    )

    assert isinstance(result, Path)
    assert result.exists()

    df = pd.read_csv(result)

    assert len(df) == 8

    assert (
        df.iloc[0]["company_id"]
        == "HAL"
    )


def test_export_csv_contains_rank():
    engine = WatchlistIntelligenceEngine()

    output_file = (
        Path("output")
        / "test_watchlist_export.csv"
    )

    try:
        engine.export_csv(
            WATCHLIST,
            YEAR,
            output_path=output_file,
        )

        df = pd.read_csv(
            output_file
        )

        assert "watchlist_rank" in df.columns

        assert (
            df["watchlist_rank"].tolist()
            == list(range(1, 9))
        )

    finally:
        if output_file.exists():
            output_file.unlink()