"""
Tests for Sprint 3 - Day 22
Portfolio Intelligence Engine.
"""

import pandas as pd
import pytest

from src.screener.portfolio_intelligence import (
    PortfolioIntelligenceEngine,
)


PORTFOLIO = [
    "TCS",
    "INFY",
    "HCLTECH",
    "LTIM",
    "RELIANCE",
    "ITC",
    "MARUTI",
    "HAL",
]

YEAR = "Mar 2024"


@pytest.fixture(scope="module")
def engine():
    return PortfolioIntelligenceEngine()


@pytest.fixture(scope="module")
def portfolio_df(engine):
    return engine.analyse_portfolio(
        PORTFOLIO,
        YEAR,
    )


# ============================================================
# Initialization
# ============================================================


def test_engine_initialization(engine):
    assert engine is not None
    assert engine.decision_engine is not None


# ============================================================
# Portfolio Analysis
# ============================================================


def test_analyse_portfolio(portfolio_df):
    assert isinstance(
        portfolio_df,
        pd.DataFrame,
    )

    assert len(portfolio_df) == 8


def test_required_columns(portfolio_df):
    required = {
        "company_id",
        "company_name",
        "broad_sector",
        "decision_score",
        "signal",
        "intelligence_score",
        "assessment",
        "portfolio_weight_pct",
    }

    assert required.issubset(
        portfolio_df.columns
    )


def test_equal_portfolio_weights(portfolio_df):
    assert (
        portfolio_df[
            "portfolio_weight_pct"
        ]
        == 12.5
    ).all()


def test_portfolio_weights_total(portfolio_df):
    total = portfolio_df[
        "portfolio_weight_pct"
    ].sum()

    assert total == pytest.approx(
        100.0
    )


def test_hal_present(portfolio_df):
    assert "HAL" in set(
        portfolio_df["company_id"]
    )


def test_reliance_present(portfolio_df):
    assert "RELIANCE" in set(
        portfolio_df["company_id"]
    )


# ============================================================
# Sector Allocation
# ============================================================


def test_sector_allocation(engine):
    result = engine.sector_allocation(
        PORTFOLIO,
        YEAR,
    )

    assert isinstance(
        result,
        pd.DataFrame,
    )

    assert len(result) == 5


def test_sector_weights_total(engine):
    result = engine.sector_allocation(
        PORTFOLIO,
        YEAR,
    )

    assert result[
        "weight_pct"
    ].sum() == pytest.approx(
        100.0
    )


def test_information_technology_weight(engine):
    result = engine.sector_allocation(
        PORTFOLIO,
        YEAR,
    )

    row = result[
        result["broad_sector"]
        == "Information Technology"
    ].iloc[0]

    assert row["company_count"] == 4

    assert row[
        "weight_pct"
    ] == pytest.approx(
        50.0
    )


def test_largest_sector_first(engine):
    result = engine.sector_allocation(
        PORTFOLIO,
        YEAR,
    )

    assert (
        result.iloc[0][
            "broad_sector"
        ]
        == "Information Technology"
    )


# ============================================================
# Signal Distribution
# ============================================================


def test_signal_distribution(engine):
    result = engine.signal_distribution(
        PORTFOLIO,
        YEAR,
    )

    assert result[
        "company_count"
    ].sum() == 8


def test_candidate_count(engine):
    result = engine.signal_distribution(
        PORTFOLIO,
        YEAR,
    )

    row = result[
        result["signal"]
        == "Candidate"
    ].iloc[0]

    assert row["company_count"] == 4


def test_strong_candidate_count(engine):
    result = engine.signal_distribution(
        PORTFOLIO,
        YEAR,
    )

    row = result[
        result["signal"]
        == "Strong Candidate"
    ].iloc[0]

    assert row["company_count"] == 1


def test_avoid_count(engine):
    result = engine.signal_distribution(
        PORTFOLIO,
        YEAR,
    )

    row = result[
        result["signal"]
        == "Avoid"
    ].iloc[0]

    assert row["company_count"] == 1


def test_signal_weights_total(engine):
    result = engine.signal_distribution(
        PORTFOLIO,
        YEAR,
    )

    assert result[
        "weight_pct"
    ].sum() == pytest.approx(
        100.0
    )


# ============================================================
# Assessment Distribution
# ============================================================


def test_assessment_distribution(engine):
    result = engine.assessment_distribution(
        PORTFOLIO,
        YEAR,
    )

    assert result[
        "company_count"
    ].sum() == 8


def test_good_assessment_count(engine):
    result = engine.assessment_distribution(
        PORTFOLIO,
        YEAR,
    )

    row = result[
        result["assessment"]
        == "Good"
    ].iloc[0]

    assert row["company_count"] == 4


def test_average_assessment_count(engine):
    result = engine.assessment_distribution(
        PORTFOLIO,
        YEAR,
    )

    row = result[
        result["assessment"]
        == "Average"
    ].iloc[0]

    assert row["company_count"] == 2


# ============================================================
# Diversification
# ============================================================


def test_diversification_score(engine):
    score = engine.diversification_score(
        PORTFOLIO,
        YEAR,
    )

    assert score == pytest.approx(
        57.5
    )


def test_diversification_valid_range(engine):
    score = engine.diversification_score(
        PORTFOLIO,
        YEAR,
    )

    assert 0 <= score <= 100


def test_concentration_risk(engine):
    risk = engine.concentration_risk(
        PORTFOLIO,
        YEAR,
    )

    assert risk == "Moderate"


# ============================================================
# Portfolio Score
# ============================================================


def test_portfolio_score(engine):
    score = engine.portfolio_score(
        PORTFOLIO,
        YEAR,
    )

    assert score == pytest.approx(
        63.33
    )


def test_portfolio_score_valid_range(engine):
    score = engine.portfolio_score(
        PORTFOLIO,
        YEAR,
    )

    assert 0 <= score <= 100


@pytest.mark.parametrize(
    "score,expected",
    [
        (100, "Strong"),
        (80, "Strong"),
        (79.99, "Healthy"),
        (65, "Healthy"),
        (64.99, "Moderate"),
        (50, "Moderate"),
        (49.99, "Weak"),
        (0, "Weak"),
        (None, "Insufficient Data"),
    ],
)
def test_health_classification(
    score,
    expected,
):
    assert (
        PortfolioIntelligenceEngine
        .classify_health(score)
        == expected
    )


# ============================================================
# Strongest / Weakest Holdings
# ============================================================


def test_strongest_holding(engine):
    result = engine.strongest_holding(
        PORTFOLIO,
        YEAR,
    )

    assert result["company_id"] == "HAL"

    assert result[
        "decision_score"
    ] == pytest.approx(
        82.84
    )


def test_weakest_holding(engine):
    result = engine.weakest_holding(
        PORTFOLIO,
        YEAR,
    )

    assert (
        result["company_id"]
        == "RELIANCE"
    )

    assert result[
        "decision_score"
    ] == pytest.approx(
        35.12
    )


# ============================================================
# Portfolio Summary
# ============================================================


def test_portfolio_summary(engine):
    result = engine.portfolio_summary(
        PORTFOLIO,
        YEAR,
    )

    assert result["company_count"] == 8
    assert result["sector_count"] == 5

    assert result[
        "portfolio_score"
    ] == pytest.approx(
        63.33
    )

    assert (
        result["portfolio_health"]
        == "Moderate"
    )


def test_summary_average_intelligence(engine):
    result = engine.portfolio_summary(
        PORTFOLIO,
        YEAR,
    )

    assert result[
        "average_intelligence_score"
    ] == pytest.approx(
        67.76
    )


def test_summary_average_decision(engine):
    result = engine.portfolio_summary(
        PORTFOLIO,
        YEAR,
    )

    assert result[
        "average_decision_score"
    ] == pytest.approx(
        62.44
    )


def test_summary_largest_sector(engine):
    result = engine.portfolio_summary(
        PORTFOLIO,
        YEAR,
    )

    assert (
        result["largest_sector"]
        == "Information Technology"
    )

    assert result[
        "largest_sector_weight_pct"
    ] == pytest.approx(
        50.0
    )


def test_summary_strongest_company(engine):
    result = engine.portfolio_summary(
        PORTFOLIO,
        YEAR,
    )

    assert (
        result["strongest_company_id"]
        == "HAL"
    )


def test_summary_weakest_company(engine):
    result = engine.portfolio_summary(
        PORTFOLIO,
        YEAR,
    )

    assert (
        result["weakest_company_id"]
        == "RELIANCE"
    )


# ============================================================
# Narrative
# ============================================================


def test_generate_summary(engine):
    result = engine.generate_summary(
        PORTFOLIO,
        YEAR,
    )

    assert isinstance(result, str)

    assert (
        "8 companies"
        in result
    )

    assert (
        "5 sectors"
        in result
    )

    assert (
        "63.33/100"
        in result
    )


def test_summary_mentions_strongest(engine):
    result = engine.generate_summary(
        PORTFOLIO,
        YEAR,
    )

    assert (
        "Hindustan Aeronautics Ltd"
        in result
    )


def test_summary_mentions_weakest(engine):
    result = engine.generate_summary(
        PORTFOLIO,
        YEAR,
    )

    assert (
        "Reliance Industries Ltd"
        in result
    )


# ============================================================
# Invalid Companies
# ============================================================


def test_invalid_company_rejected(engine):
    with pytest.raises(
        (ValueError, KeyError),
    ):
        engine.analyse_portfolio(
            [
                "TCS",
                "INVALID_COMPANY",
            ],
            YEAR,
        )


def test_ignore_invalid_company(engine):
    result = engine.analyse_portfolio(
        [
            "TCS",
            "INVALID_COMPANY",
        ],
        YEAR,
        ignore_invalid=True,
    )

    assert len(result) == 1

    assert (
        result.iloc[0]["company_id"]
        == "TCS"
    )


def test_all_invalid_companies_rejected(engine):
    with pytest.raises(ValueError):
        engine.analyse_portfolio(
            [
                "INVALID_A",
                "INVALID_B",
            ],
            YEAR,
            ignore_invalid=True,
        )


# ============================================================
# CSV Export
# ============================================================


def test_export_csv(engine, tmp_path):
    output = (
        tmp_path
        / "portfolio_test.csv"
    )

    result = engine.export_csv(
        PORTFOLIO,
        YEAR,
        output_path=output,
    )

    assert result.exists()


def test_export_csv_row_count(
    engine,
    tmp_path,
):
    output = (
        tmp_path
        / "portfolio_test.csv"
    )

    engine.export_csv(
        PORTFOLIO,
        YEAR,
        output_path=output,
    )

    df = pd.read_csv(output)

    assert len(df) == 8


def test_export_csv_contains_weight(
    engine,
    tmp_path,
):
    output = (
        tmp_path
        / "portfolio_test.csv"
    )

    engine.export_csv(
        PORTFOLIO,
        YEAR,
        output_path=output,
    )

    df = pd.read_csv(output)

    assert (
        "portfolio_weight_pct"
        in df.columns
    )

# ============================================================
# Day 26 - Custom Portfolio Weights
# ============================================================


def test_custom_portfolio_weights(engine):
    result = engine.analyse_portfolio(
        ["HAL", "TCS"],
        YEAR,
        weights={
            "HAL": 70,
            "TCS": 30,
        },
    )

    weights = dict(
        zip(
            result["company_id"],
            result["portfolio_weight_pct"],
        )
    )

    assert weights["HAL"] == 70.0
    assert weights["TCS"] == 30.0


def test_custom_weights_must_total_100(engine):
    with pytest.raises(
        ValueError,
        match="must total 100",
    ):
        engine.analyse_portfolio(
            ["HAL", "TCS"],
            YEAR,
            weights={
                "HAL": 60,
                "TCS": 30,
            },
        )


def test_negative_custom_weight_rejected(engine):
    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        engine.analyse_portfolio(
            ["HAL", "TCS"],
            YEAR,
            weights={
                "HAL": 110,
                "TCS": -10,
            },
        )


def test_missing_custom_weight_rejected(engine):
    with pytest.raises(
        ValueError,
        match="Missing portfolio weights",
    ):
        engine.analyse_portfolio(
            ["HAL", "TCS"],
            YEAR,
            weights={
                "HAL": 100,
            },
        )


def test_custom_weight_sector_allocation(engine):
    result = engine.sector_allocation(
        ["HAL", "TCS"],
        YEAR,
        weights={
            "HAL": 70,
            "TCS": 30,
        },
    )

    allocation = dict(
        zip(
            result["broad_sector"],
            result["weight_pct"],
        )
    )

    assert allocation["Industrials"] == 70.0
    assert (
        allocation["Information Technology"]
        == 30.0
    )


def test_custom_weight_concentration_risk(engine):
    result = engine.concentration_risk(
        ["HAL", "TCS"],
        YEAR,
        weights={
            "HAL": 70,
            "TCS": 30,
        },
    )

    assert result == "High"


def test_custom_weight_portfolio_score(engine):
    equal_score = engine.portfolio_score(
        ["HAL", "TCS"],
        YEAR,
    )

    weighted_score = engine.portfolio_score(
        ["HAL", "TCS"],
        YEAR,
        weights={
            "HAL": 70,
            "TCS": 30,
        },
    )

    assert equal_score == 80.0
    assert weighted_score == 79.86


def test_equal_weight_backward_compatibility(engine):
    result = engine.analyse_portfolio(
        ["HAL", "TCS"],
        YEAR,
    )

    assert (
        result["portfolio_weight_pct"]
        .tolist()
        == [50.0, 50.0]
    )


def test_custom_weight_summary(engine):
    summary = engine.portfolio_summary(
        ["HAL", "TCS"],
        YEAR,
        weights={
            "HAL": 70,
            "TCS": 30,
        },
    )

    assert summary["portfolio_score"] == 79.86
    assert (
        summary["largest_sector_weight_pct"]
        == 70.0
    )
    assert summary["concentration_risk"] == "High"


def test_custom_weight_export_csv(
    engine,
    tmp_path,
):
    output = tmp_path / "weighted_portfolio.csv"

    engine.export_csv(
        ["HAL", "TCS"],
        YEAR,
        output_path=output,
        weights={
            "HAL": 70,
            "TCS": 30,
        },
    )

    df = pd.read_csv(output)

    weights = dict(
        zip(
            df["company_id"],
            df["portfolio_weight_pct"],
        )
    )

    assert weights["HAL"] == 70.0
    assert weights["TCS"] == 30.0
