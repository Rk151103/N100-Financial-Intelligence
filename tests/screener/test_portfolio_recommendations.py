"""
Tests for Sprint 3 - Day 23
Portfolio Risk & Recommendation Engine.
"""

import pandas as pd
import pytest

from src.screener.portfolio_recommendations import (
    PortfolioRecommendationEngine,
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
    return PortfolioRecommendationEngine()


@pytest.fixture(scope="module")
def recommendations(engine):
    return engine.holding_recommendations(
        PORTFOLIO,
        YEAR,
    )


# ============================================================
# Initialization
# ============================================================


def test_engine_initialization(engine):
    assert engine is not None
    assert engine.portfolio_engine is not None


# ============================================================
# Normalization
# ============================================================


def test_normalize_company_ids():
    result = (
        PortfolioRecommendationEngine
        ._normalize_company_ids(
            ["tcs", " INFY ", "TCS", None, ""]
        )
    )

    assert result == ["TCS", "INFY"]


def test_none_portfolio_rejected():
    with pytest.raises(ValueError):
        (
            PortfolioRecommendationEngine
            ._normalize_company_ids(None)
        )


def test_empty_portfolio_rejected():
    with pytest.raises(ValueError):
        (
            PortfolioRecommendationEngine
            ._normalize_company_ids([])
        )


# ============================================================
# Action Classification
# ============================================================


@pytest.mark.parametrize(
    "signal,score,expected",
    [
        ("Strong Candidate", 90, "Maintain"),
        ("Candidate", 70, "Maintain"),
        ("Watch", 55, "Review"),
        ("Avoid", 40, "Reduce Exposure"),
        ("Unknown", 60, "Review"),
        ("Candidate", None, "Review"),
    ],
)
def test_action_classification(
    signal,
    score,
    expected,
):
    assert (
        PortfolioRecommendationEngine
        .classify_action(
            signal,
            score,
        )
        == expected
    )


# ============================================================
# Priority Classification
# ============================================================


@pytest.mark.parametrize(
    "signal,score,expected",
    [
        ("Avoid", 60, "High"),
        ("Candidate", 49, "High"),
        ("Watch", 60, "Medium"),
        ("Candidate", 60, "Medium"),
        ("Candidate", 65, "Low"),
        ("Strong Candidate", 90, "Low"),
        ("Candidate", None, "Medium"),
    ],
)
def test_priority_classification(
    signal,
    score,
    expected,
):
    assert (
        PortfolioRecommendationEngine
        .classify_priority(
            signal,
            score,
        )
        == expected
    )


# ============================================================
# Holding Recommendations
# ============================================================


def test_holding_recommendations_dataframe(
    recommendations,
):
    assert isinstance(
        recommendations,
        pd.DataFrame,
    )


def test_holding_count(recommendations):
    assert len(recommendations) == 8


def test_required_columns(recommendations):
    required = {
        "recommendation_rank",
        "company_id",
        "company_name",
        "decision_score",
        "signal",
        "recommended_action",
        "priority",
        "recommendation_reason",
    }

    assert required.issubset(
        recommendations.columns
    )


def test_recommendation_rank_sequence(
    recommendations,
):
    assert recommendations[
        "recommendation_rank"
    ].tolist() == list(
        range(1, 9)
    )


def test_reliance_rank_one(recommendations):
    assert (
        recommendations.iloc[0]["company_id"]
        == "RELIANCE"
    )


def test_reliance_reduce_exposure(
    recommendations,
):
    row = recommendations[
        recommendations["company_id"]
        == "RELIANCE"
    ].iloc[0]

    assert (
        row["recommended_action"]
        == "Reduce Exposure"
    )

    assert row["priority"] == "High"


def test_maruti_review(recommendations):
    row = recommendations[
        recommendations["company_id"]
        == "MARUTI"
    ].iloc[0]

    assert row["recommended_action"] == "Review"
    assert row["priority"] == "Medium"


def test_hcltech_review(recommendations):
    row = recommendations[
        recommendations["company_id"]
        == "HCLTECH"
    ].iloc[0]

    assert row["recommended_action"] == "Review"
    assert row["priority"] == "Medium"


def test_hal_maintain(recommendations):
    row = recommendations[
        recommendations["company_id"]
        == "HAL"
    ].iloc[0]

    assert (
        row["recommended_action"]
        == "Maintain"
    )

    assert row["priority"] == "Low"


def test_candidate_holdings_maintain(
    recommendations,
):
    candidate_rows = recommendations[
        recommendations["signal"]
        == "Candidate"
    ]

    assert (
        candidate_rows[
            "recommended_action"
        ]
        == "Maintain"
    ).all()


# ============================================================
# Recommendation Reasons
# ============================================================


def test_recommendation_reason_not_empty(
    recommendations,
):
    assert recommendations[
        "recommendation_reason"
    ].notna().all()

    assert (
        recommendations[
            "recommendation_reason"
        ].str.len()
        > 0
    ).all()


def test_avoid_reason(recommendations):
    row = recommendations[
        recommendations["company_id"]
        == "RELIANCE"
    ].iloc[0]

    assert "Weak analytical" in row[
        "recommendation_reason"
    ]


# ============================================================
# Sector Risk
# ============================================================


def test_sector_risk_analysis(engine):
    result = engine.sector_risk_analysis(
        PORTFOLIO,
        YEAR,
    )

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 5


def test_sector_risk_required_columns(engine):
    result = engine.sector_risk_analysis(
        PORTFOLIO,
        YEAR,
    )

    required = {
        "broad_sector",
        "company_count",
        "weight_pct",
        "concentration_risk",
        "recommendation",
    }

    assert required.issubset(
        result.columns
    )


def test_information_technology_high_risk(
    engine,
):
    result = engine.sector_risk_analysis(
        PORTFOLIO,
        YEAR,
    )

    row = result[
        result["broad_sector"]
        == "Information Technology"
    ].iloc[0]

    assert row["weight_pct"] == pytest.approx(
        50.0
    )

    assert (
        row["concentration_risk"]
        == "High"
    )

    assert (
        row["recommendation"]
        == "Diversify sector exposure"
    )


def test_other_sectors_low_risk(engine):
    result = engine.sector_risk_analysis(
        PORTFOLIO,
        YEAR,
    )

    other = result[
        result["broad_sector"]
        != "Information Technology"
    ]

    assert (
        other["concentration_risk"]
        == "Low"
    ).all()


# ============================================================
# Action Distribution
# ============================================================


def test_action_distribution(engine):
    result = engine.action_distribution(
        PORTFOLIO,
        YEAR,
    )

    assert result["company_count"].sum() == 8


def test_maintain_count(engine):
    result = engine.action_distribution(
        PORTFOLIO,
        YEAR,
    )

    row = result[
        result["recommended_action"]
        == "Maintain"
    ].iloc[0]

    assert row["company_count"] == 5


def test_review_count(engine):
    result = engine.action_distribution(
        PORTFOLIO,
        YEAR,
    )

    row = result[
        result["recommended_action"]
        == "Review"
    ].iloc[0]

    assert row["company_count"] == 2


def test_reduce_exposure_count(engine):
    result = engine.action_distribution(
        PORTFOLIO,
        YEAR,
    )

    row = result[
        result["recommended_action"]
        == "Reduce Exposure"
    ].iloc[0]

    assert row["company_count"] == 1


def test_action_weights_total(engine):
    result = engine.action_distribution(
        PORTFOLIO,
        YEAR,
    )

    assert result[
        "weight_pct"
    ].sum() == pytest.approx(
        100.0
    )


# ============================================================
# Priority Distribution
# ============================================================


def test_priority_distribution(engine):
    result = engine.priority_distribution(
        PORTFOLIO,
        YEAR,
    )

    assert result["company_count"].sum() == 8


def test_high_priority_count(engine):
    result = engine.priority_distribution(
        PORTFOLIO,
        YEAR,
    )

    row = result[
        result["priority"] == "High"
    ].iloc[0]

    assert row["company_count"] == 1


def test_medium_priority_count(engine):
    result = engine.priority_distribution(
        PORTFOLIO,
        YEAR,
    )

    row = result[
        result["priority"] == "Medium"
    ].iloc[0]

    assert row["company_count"] == 2


def test_low_priority_count(engine):
    result = engine.priority_distribution(
        PORTFOLIO,
        YEAR,
    )

    row = result[
        result["priority"] == "Low"
    ].iloc[0]

    assert row["company_count"] == 5


def test_priority_order(engine):
    result = engine.priority_distribution(
        PORTFOLIO,
        YEAR,
    )

    assert result["priority"].tolist() == [
        "High",
        "Medium",
        "Low",
    ]


# ============================================================
# Portfolio-Level Recommendations
# ============================================================


def test_portfolio_recommendations(engine):
    result = engine.portfolio_recommendations(
        PORTFOLIO,
        YEAR,
    )

    assert isinstance(result, list)
    assert len(result) == 5


def test_recommendations_include_diversification(
    engine,
):
    result = engine.portfolio_recommendations(
        PORTFOLIO,
        YEAR,
    )

    text = " ".join(result)

    assert "Diversify" in text
    assert "Information Technology" in text


def test_recommendations_include_reliance(
    engine,
):
    result = engine.portfolio_recommendations(
        PORTFOLIO,
        YEAR,
    )

    text = " ".join(result)

    assert "Reliance Industries Ltd" in text


def test_recommendations_include_watch_holdings(
    engine,
):
    result = engine.portfolio_recommendations(
        PORTFOLIO,
        YEAR,
    )

    text = " ".join(result)

    assert "Maruti Suzuki India Ltd" in text
    assert "HCL Technologies Ltd" in text


def test_recommendations_include_hal(engine):
    result = engine.portfolio_recommendations(
        PORTFOLIO,
        YEAR,
    )

    text = " ".join(result)

    assert "Hindustan Aeronautics Ltd" in text


# ============================================================
# Recommendation Summary
# ============================================================


def test_recommendation_summary(engine):
    result = engine.recommendation_summary(
        PORTFOLIO,
        YEAR,
    )

    assert result["company_count"] == 8

    assert result[
        "portfolio_score"
    ] == pytest.approx(63.33)

    assert (
        result["portfolio_health"]
        == "Moderate"
    )


def test_summary_action_counts(engine):
    result = engine.recommendation_summary(
        PORTFOLIO,
        YEAR,
    )

    assert result["maintain_count"] == 5
    assert result["review_count"] == 2

    assert (
        result["reduce_exposure_count"]
        == 1
    )


def test_summary_priority_counts(engine):
    result = engine.recommendation_summary(
        PORTFOLIO,
        YEAR,
    )

    assert result["high_priority_count"] == 1
    assert result["medium_priority_count"] == 2
    assert result["low_priority_count"] == 5


def test_summary_largest_sector(engine):
    result = engine.recommendation_summary(
        PORTFOLIO,
        YEAR,
    )

    assert (
        result["largest_sector"]
        == "Information Technology"
    )

    assert result[
        "largest_sector_weight_pct"
    ] == pytest.approx(50.0)


def test_highest_priority_company(engine):
    result = engine.recommendation_summary(
        PORTFOLIO,
        YEAR,
    )

    assert (
        result["highest_priority_company"]
        == "Reliance Industries Ltd"
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
    assert "8 companies" in result
    assert "Moderate" in result
    assert "63.33/100" in result


def test_summary_mentions_sector(engine):
    result = engine.generate_summary(
        PORTFOLIO,
        YEAR,
    )

    assert "Information Technology" in result
    assert "50.0%" in result


def test_summary_mentions_high_priority(engine):
    result = engine.generate_summary(
        PORTFOLIO,
        YEAR,
    )

    assert (
        "1 holding(s)"
        in result
    )


# ============================================================
# Invalid Companies
# ============================================================


def test_invalid_company_rejected(engine):
    with pytest.raises(
        (ValueError, KeyError),
    ):
        engine.holding_recommendations(
            [
                "TCS",
                "INVALID_COMPANY",
            ],
            YEAR,
        )


def test_ignore_invalid_company(engine):
    result = engine.holding_recommendations(
        [
            "TCS",
            "INVALID_COMPANY",
        ],
        YEAR,
        ignore_invalid=True,
    )

    assert len(result) == 1
    assert result.iloc[0]["company_id"] == "TCS"


def test_duplicates_removed(engine):
    result = engine.holding_recommendations(
        [
            "TCS",
            "TCS",
            "INFY",
            "INFY",
        ],
        YEAR,
    )

    assert len(result) == 2

    assert set(result["company_id"]) == {
        "TCS",
        "INFY",
    }


# ============================================================
# CSV Export
# ============================================================


def test_export_csv(engine, tmp_path):
    output = (
        tmp_path
        / "recommendations.csv"
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
        / "recommendations.csv"
    )

    engine.export_csv(
        PORTFOLIO,
        YEAR,
        output_path=output,
    )

    df = pd.read_csv(output)

    assert len(df) == 8


def test_export_csv_columns(
    engine,
    tmp_path,
):
    output = (
        tmp_path
        / "recommendations.csv"
    )

    engine.export_csv(
        PORTFOLIO,
        YEAR,
        output_path=output,
    )

    df = pd.read_csv(output)

    assert "recommended_action" in df.columns
    assert "priority" in df.columns

    assert (
        "recommendation_reason"
        in df.columns
    )