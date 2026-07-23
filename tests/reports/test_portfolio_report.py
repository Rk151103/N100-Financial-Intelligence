"""
Sprint 3 - Day 24
Tests for Portfolio Intelligence Report Generator.
"""

import pandas as pd
import pytest

from src.reports.portfolio_report import (
    PortfolioReportGenerator,
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
def generator():
    return PortfolioReportGenerator()


@pytest.fixture(scope="module")
def holdings(generator):
    return generator.holding_report(PORTFOLIO, YEAR)


@pytest.fixture(scope="module")
def sectors(generator):
    return generator.sector_report(PORTFOLIO, YEAR)


@pytest.fixture(scope="module")
def summary(generator):
    return generator.executive_summary(PORTFOLIO, YEAR)


# ============================================================
# Initialization
# ============================================================


def test_generator_initialization(generator):
    assert generator is not None
    assert generator.portfolio_engine is not None
    assert generator.recommendation_engine is not None


# ============================================================
# Normalization
# ============================================================


def test_normalize_company_ids():
    result = PortfolioReportGenerator._normalize_company_ids(
        ["tcs", " INFY ", "TCS", None, ""]
    )

    assert result == ["TCS", "INFY"]


def test_none_portfolio_rejected():
    with pytest.raises(ValueError):
        PortfolioReportGenerator._normalize_company_ids(None)


def test_empty_portfolio_rejected():
    with pytest.raises(ValueError):
        PortfolioReportGenerator._normalize_company_ids([])


def test_blank_portfolio_rejected():
    with pytest.raises(ValueError):
        PortfolioReportGenerator._normalize_company_ids(
            ["", " ", None]
        )


# ============================================================
# Holding Report
# ============================================================


def test_holding_report_dataframe(holdings):
    assert isinstance(holdings, pd.DataFrame)


def test_holding_count(holdings):
    assert len(holdings) == 8


def test_holding_required_columns(holdings):
    required = {
        "report_rank",
        "company_id",
        "company_name",
        "broad_sector",
        "decision_score",
        "signal",
        "recommended_action",
        "priority",
        "portfolio_weight_pct",
    }

    assert required.issubset(holdings.columns)


def test_report_rank_sequence(holdings):
    assert holdings["report_rank"].tolist() == list(
        range(1, 9)
    )


def test_holdings_sorted_by_decision_score(holdings):
    scores = holdings["decision_score"].tolist()

    assert scores == sorted(scores, reverse=True)


def test_hal_is_first_holding(holdings):
    assert holdings.iloc[0]["company_id"] == "HAL"


def test_reliance_is_last_holding(holdings):
    assert holdings.iloc[-1]["company_id"] == "RELIANCE"


def test_hal_decision_score(holdings):
    row = holdings[
        holdings["company_id"] == "HAL"
    ].iloc[0]

    assert row["decision_score"] == pytest.approx(82.84)


def test_tcs_decision_score(holdings):
    row = holdings[
        holdings["company_id"] == "TCS"
    ].iloc[0]

    assert row["decision_score"] == pytest.approx(71.41)


def test_reliance_decision_score(holdings):
    row = holdings[
        holdings["company_id"] == "RELIANCE"
    ].iloc[0]

    assert row["decision_score"] == pytest.approx(35.12)


def test_hal_recommendation(holdings):
    row = holdings[
        holdings["company_id"] == "HAL"
    ].iloc[0]

    assert row["signal"] == "Strong Candidate"
    assert row["recommended_action"] == "Maintain"
    assert row["priority"] == "Low"


def test_reliance_recommendation(holdings):
    row = holdings[
        holdings["company_id"] == "RELIANCE"
    ].iloc[0]

    assert row["signal"] == "Avoid"
    assert row["recommended_action"] == "Reduce Exposure"
    assert row["priority"] == "High"


def test_watch_holdings_review(holdings):
    watch = holdings[
        holdings["company_id"].isin(
            ["HCLTECH", "MARUTI"]
        )
    ]

    assert (watch["signal"] == "Watch").all()
    assert (
        watch["recommended_action"] == "Review"
    ).all()

    assert (watch["priority"] == "Medium").all()


def test_equal_portfolio_weights(holdings):
    assert (
        holdings["portfolio_weight_pct"] == 12.5
    ).all()


def test_portfolio_weights_total(holdings):
    assert holdings[
        "portfolio_weight_pct"
    ].sum() == pytest.approx(100.0)


# ============================================================
# Sector Report
# ============================================================


def test_sector_report_dataframe(sectors):
    assert isinstance(sectors, pd.DataFrame)


def test_sector_count(sectors):
    assert len(sectors) == 5


def test_sector_required_columns(sectors):
    required = {
        "broad_sector",
        "company_count",
        "weight_pct",
        "concentration_risk",
        "recommendation",
    }

    assert required.issubset(sectors.columns)


def test_sector_weights_total(sectors):
    assert sectors["weight_pct"].sum() == pytest.approx(
        100.0
    )


def test_information_technology_sector(sectors):
    row = sectors[
        sectors["broad_sector"]
        == "Information Technology"
    ].iloc[0]

    assert row["company_count"] == 4
    assert row["weight_pct"] == pytest.approx(50.0)
    assert row["concentration_risk"] == "High"

    assert (
        row["recommendation"]
        == "Diversify sector exposure"
    )


def test_other_sector_weights(sectors):
    other = sectors[
        sectors["broad_sector"]
        != "Information Technology"
    ]

    assert (other["company_count"] == 1).all()
    assert (other["weight_pct"] == 12.5).all()


def test_other_sector_risk_low(sectors):
    other = sectors[
        sectors["broad_sector"]
        != "Information Technology"
    ]

    assert (
        other["concentration_risk"] == "Low"
    ).all()


def test_largest_sector_first(sectors):
    assert (
        sectors.iloc[0]["broad_sector"]
        == "Information Technology"
    )


# ============================================================
# Executive Summary
# ============================================================


def test_summary_is_dictionary(summary):
    assert isinstance(summary, dict)


def test_summary_company_count(summary):
    assert summary["company_count"] == 8


def test_summary_sector_count(summary):
    assert summary["sector_count"] == 5


def test_summary_portfolio_score(summary):
    assert summary["portfolio_score"] == pytest.approx(
        63.33
    )


def test_summary_portfolio_health(summary):
    assert summary["portfolio_health"] == "Moderate"


def test_summary_average_intelligence(summary):
    assert summary[
        "average_intelligence_score"
    ] == pytest.approx(67.76)


def test_summary_average_decision(summary):
    assert summary[
        "average_decision_score"
    ] == pytest.approx(62.44)


def test_summary_diversification(summary):
    assert summary[
        "diversification_score"
    ] == pytest.approx(57.5)


def test_summary_concentration_risk(summary):
    assert summary["concentration_risk"] == "Moderate"


def test_summary_largest_sector(summary):
    assert (
        summary["largest_sector"]
        == "Information Technology"
    )

    assert summary[
        "largest_sector_weight_pct"
    ] == pytest.approx(50.0)


def test_summary_strongest_company(summary):
    assert summary["strongest_company_id"] == "HAL"

    assert (
        summary["strongest_company_name"]
        == "Hindustan Aeronautics Ltd"
    )

    assert summary[
        "strongest_decision_score"
    ] == pytest.approx(82.84)


def test_summary_weakest_company(summary):
    assert summary["weakest_company_id"] == "RELIANCE"

    assert (
        summary["weakest_company_name"]
        == "Reliance Industries Ltd"
    )

    assert summary[
        "weakest_decision_score"
    ] == pytest.approx(35.12)


def test_summary_action_counts(summary):
    assert summary["maintain_count"] == 5
    assert summary["review_count"] == 2
    assert summary["reduce_exposure_count"] == 1


def test_summary_priority_counts(summary):
    assert summary["high_priority_count"] == 1
    assert summary["medium_priority_count"] == 2
    assert summary["low_priority_count"] == 5


# ============================================================
# Recommendations
# ============================================================


def test_recommendations(generator):
    result = generator.recommendations(
        PORTFOLIO,
        YEAR,
    )

    assert isinstance(result, list)
    assert len(result) == 5


def test_recommendations_sector(generator):
    result = generator.recommendations(
        PORTFOLIO,
        YEAR,
    )

    text = " ".join(result)

    assert "Information Technology" in text
    assert "50.0%" in text


def test_recommendations_reliance(generator):
    result = generator.recommendations(
        PORTFOLIO,
        YEAR,
    )

    text = " ".join(result)

    assert "Reliance Industries Ltd" in text


def test_recommendations_hal(generator):
    result = generator.recommendations(
        PORTFOLIO,
        YEAR,
    )

    text = " ".join(result)

    assert "Hindustan Aeronautics Ltd" in text


# ============================================================
# Narrative
# ============================================================


def test_generate_narrative(generator):
    result = generator.generate_narrative(
        PORTFOLIO,
        YEAR,
    )

    assert isinstance(result, str)
    assert "8 companies" in result
    assert "5 sectors" in result
    assert "Mar 2024" in result


def test_narrative_portfolio_score(generator):
    result = generator.generate_narrative(
        PORTFOLIO,
        YEAR,
    )

    assert "63.33/100" in result
    assert "Moderate" in result


def test_narrative_diversification(generator):
    result = generator.generate_narrative(
        PORTFOLIO,
        YEAR,
    )

    assert "57.5/100" in result
    assert "moderate concentration risk" in result


def test_narrative_largest_sector(generator):
    result = generator.generate_narrative(
        PORTFOLIO,
        YEAR,
    )

    assert "Information Technology" in result
    assert "50.0%" in result


def test_narrative_strongest_and_weakest(generator):
    result = generator.generate_narrative(
        PORTFOLIO,
        YEAR,
    )

    assert "Hindustan Aeronautics Ltd" in result
    assert "Reliance Industries Ltd" in result


def test_narrative_high_priority(generator):
    result = generator.generate_narrative(
        PORTFOLIO,
        YEAR,
    )

    assert "1 holding(s)" in result


# ============================================================
# Complete Report
# ============================================================


def test_generate_report(generator):
    result = generator.generate_report(
        PORTFOLIO,
        YEAR,
    )

    assert isinstance(result, dict)

    assert set(result.keys()) == {
        "summary",
        "holdings",
        "sectors",
        "recommendations",
        "narrative",
    }


def test_complete_report_components(generator):
    result = generator.generate_report(
        PORTFOLIO,
        YEAR,
    )

    assert isinstance(result["summary"], dict)
    assert isinstance(result["holdings"], pd.DataFrame)
    assert isinstance(result["sectors"], pd.DataFrame)
    assert isinstance(result["recommendations"], list)
    assert isinstance(result["narrative"], str)


# ============================================================
# Invalid / Duplicate Companies
# ============================================================


def test_invalid_company_rejected(generator):
    with pytest.raises((ValueError, KeyError)):
        generator.holding_report(
            ["TCS", "INVALID_COMPANY"],
            YEAR,
        )


def test_ignore_invalid_company(generator):
    result = generator.holding_report(
        ["TCS", "INVALID_COMPANY"],
        YEAR,
        ignore_invalid=True,
    )

    assert len(result) == 1
    assert result.iloc[0]["company_id"] == "TCS"


def test_duplicate_companies_removed(generator):
    result = generator.holding_report(
        ["TCS", "TCS", "INFY", "INFY"],
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


def test_export_csv(generator, tmp_path):
    output = tmp_path / "portfolio_report.csv"

    result = generator.export_csv(
        PORTFOLIO,
        YEAR,
        output_path=output,
    )

    assert result.exists()


def test_export_csv_row_count(generator, tmp_path):
    output = tmp_path / "portfolio_report.csv"

    generator.export_csv(
        PORTFOLIO,
        YEAR,
        output_path=output,
    )

    df = pd.read_csv(output)

    assert len(df) == 8


def test_export_csv_contains_report_rank(
    generator,
    tmp_path,
):
    output = tmp_path / "portfolio_report.csv"

    generator.export_csv(
        PORTFOLIO,
        YEAR,
        output_path=output,
    )

    df = pd.read_csv(output)

    assert "report_rank" in df.columns


def test_export_csv_contains_recommendations(
    generator,
    tmp_path,
):
    output = tmp_path / "portfolio_report.csv"

    generator.export_csv(
        PORTFOLIO,
        YEAR,
        output_path=output,
    )

    df = pd.read_csv(output)

    assert "recommended_action" in df.columns
    assert "priority" in df.columns


def test_export_csv_decision_order(
    generator,
    tmp_path,
):
    output = tmp_path / "portfolio_report.csv"

    generator.export_csv(
        PORTFOLIO,
        YEAR,
        output_path=output,
    )

    df = pd.read_csv(output)

    assert df.iloc[0]["company_id"] == "HAL"
    assert df.iloc[-1]["company_id"] == "RELIANCE"