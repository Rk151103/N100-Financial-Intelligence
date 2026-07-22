"""
tests/screener/test_company_intelligence.py

N100 Financial Intelligence Platform
Sprint 3 - Day 19
Company Intelligence Engine Tests
"""

import pandas as pd
import pytest

from src.screener.company_intelligence import (
    CompanyIntelligenceEngine,
)


YEAR = "Mar 2024"


# =========================================================
# Initialization
# =========================================================

def test_engine_initialization():
    engine = CompanyIntelligenceEngine()

    assert engine.db_path.exists()
    assert engine.ranking_engine is not None


# =========================================================
# Real Database Loading
# =========================================================

def test_load_tcs_data():
    engine = CompanyIntelligenceEngine()

    row = engine.load_company_data(
        "TCS",
        YEAR,
    )

    assert row["company_id"] == "TCS"
    assert row["year"] == YEAR
    assert row["broad_sector"] == "Information Technology"


def test_company_id_case_insensitive():
    engine = CompanyIntelligenceEngine()

    row = engine.load_company_data(
        "tcs",
        YEAR,
    )

    assert row["company_id"] == "TCS"


def test_invalid_company():
    engine = CompanyIntelligenceEngine()

    with pytest.raises(ValueError):
        engine.load_company_data(
            "INVALID_COMPANY",
            YEAR,
        )


# =========================================================
# Strength Detection
# =========================================================

def test_strength_detection():
    engine = CompanyIntelligenceEngine()

    row = pd.Series(
        {
            "return_on_equity_pct": 25,
            "operating_profit_margin_pct": 22,
            "revenue_cagr_5yr": 15,
            "pat_cagr_5yr": 14,
            "eps_cagr_5yr": 13,
            "debt_to_equity": 0.3,
            "broad_sector": "Industrials",
            "interest_coverage": 8,
            "free_cash_flow_cr": 100,
            "asset_turnover": 1.5,
        }
    )

    strengths = engine.identify_strengths(row)

    assert "Strong return on equity" in strengths
    assert "Strong operating profitability" in strengths
    assert "Healthy revenue growth" in strengths
    assert "Healthy profit growth" in strengths
    assert "Healthy EPS growth" in strengths
    assert "Conservative leverage" in strengths
    assert "Strong interest coverage" in strengths
    assert "Positive free cash flow" in strengths
    assert "Efficient asset utilization" in strengths


def test_no_strengths():
    engine = CompanyIntelligenceEngine()

    row = pd.Series(
        {
            "return_on_equity_pct": 15,
            "operating_profit_margin_pct": 15,
            "revenue_cagr_5yr": 5,
            "pat_cagr_5yr": 5,
            "eps_cagr_5yr": 5,
            "debt_to_equity": 1,
            "broad_sector": "Industrials",
            "interest_coverage": 3,
            "free_cash_flow_cr": 0,
            "asset_turnover": 0.8,
        }
    )

    assert engine.identify_strengths(row) == []


# =========================================================
# Risk Detection
# =========================================================

def test_risk_detection():
    engine = CompanyIntelligenceEngine()

    row = pd.Series(
        {
            "return_on_equity_pct": 5,
            "operating_profit_margin_pct": 5,
            "revenue_cagr_5yr": -5,
            "pat_cagr_5yr": -10,
            "eps_cagr_5yr": -8,
            "debt_to_equity": 3,
            "broad_sector": "Industrials",
            "interest_coverage": 1.5,
            "free_cash_flow_cr": -50,
            "asset_turnover": 0.3,
        }
    )

    risks = engine.identify_risks(row)

    assert "Low return on equity" in risks
    assert "Weak operating margin" in risks
    assert "Revenue contraction" in risks
    assert "Profit contraction" in risks
    assert "EPS contraction" in risks
    assert "High financial leverage" in risks
    assert "Weak interest coverage" in risks
    assert "Negative free cash flow" in risks
    assert "Low asset utilization" in risks


def test_financial_sector_debt_exemption():
    engine = CompanyIntelligenceEngine()

    row = pd.Series(
        {
            "return_on_equity_pct": 15,
            "operating_profit_margin_pct": 15,
            "revenue_cagr_5yr": 5,
            "pat_cagr_5yr": 5,
            "eps_cagr_5yr": 5,
            "debt_to_equity": 10,
            "broad_sector": "Financials",
            "interest_coverage": 3,
            "free_cash_flow_cr": 10,
            "asset_turnover": 0.8,
        }
    )

    risks = engine.identify_risks(row)

    assert "High financial leverage" not in risks


def test_financial_sector_not_given_low_debt_strength():
    engine = CompanyIntelligenceEngine()

    row = pd.Series(
        {
            "return_on_equity_pct": 15,
            "operating_profit_margin_pct": 15,
            "revenue_cagr_5yr": 5,
            "pat_cagr_5yr": 5,
            "eps_cagr_5yr": 5,
            "debt_to_equity": 0.1,
            "broad_sector": "Financials",
            "interest_coverage": 3,
            "free_cash_flow_cr": 0,
            "asset_turnover": 0.8,
        }
    )

    strengths = engine.identify_strengths(row)

    assert "Conservative leverage" not in strengths


# =========================================================
# Classification
# =========================================================

@pytest.mark.parametrize(
    "score, expected",
    [
        (90, "Strong"),
        (80, "Strong"),
        (79.99, "Good"),
        (65, "Good"),
        (64.99, "Average"),
        (50, "Average"),
        (49.99, "Weak"),
        (10, "Weak"),
        (None, "Insufficient Data"),
    ],
)
def test_score_classification(score, expected):
    assert (
        CompanyIntelligenceEngine.classify_score(score)
        == expected
    )


# =========================================================
# Intelligence Score
# =========================================================

def test_intelligence_score_strength_bonus():
    result = (
        CompanyIntelligenceEngine
        .calculate_intelligence_score(
            ranking_score=60,
            strengths=["A", "B"],
            risks=[],
        )
    )

    # Two strengths = +3
    assert result == 63.0


def test_intelligence_score_risk_penalty():
    result = (
        CompanyIntelligenceEngine
        .calculate_intelligence_score(
            ranking_score=60,
            strengths=[],
            risks=["A", "B"],
        )
    )

    # Two risks = -4
    assert result == 56.0


def test_strength_bonus_capped_at_ten():
    strengths = [
        str(i)
        for i in range(20)
    ]

    result = (
        CompanyIntelligenceEngine
        .calculate_intelligence_score(
            ranking_score=50,
            strengths=strengths,
            risks=[],
        )
    )

    assert result == 60.0


def test_risk_penalty_capped_at_ten():
    risks = [
        str(i)
        for i in range(20)
    ]

    result = (
        CompanyIntelligenceEngine
        .calculate_intelligence_score(
            ranking_score=50,
            strengths=[],
            risks=risks,
        )
    )

    assert result == 40.0


def test_intelligence_score_upper_bound():
    result = (
        CompanyIntelligenceEngine
        .calculate_intelligence_score(
            ranking_score=99,
            strengths=["A"] * 20,
            risks=[],
        )
    )

    assert result == 100


def test_intelligence_score_lower_bound():
    result = (
        CompanyIntelligenceEngine
        .calculate_intelligence_score(
            ranking_score=2,
            strengths=[],
            risks=["A"] * 20,
        )
    )

    assert result == 0


def test_intelligence_score_none():
    result = (
        CompanyIntelligenceEngine
        .calculate_intelligence_score(
            ranking_score=None,
            strengths=["A"],
            risks=["B"],
        )
    )

    assert result is None


# =========================================================
# Real TCS Integration
# =========================================================

def test_tcs_analysis():
    engine = CompanyIntelligenceEngine()

    result = engine.analyse_company(
        "TCS",
        YEAR,
    )

    assert result["company_id"] == "TCS"
    assert result["overall_rank"] == 14
    assert result["sector_rank"] == 1
    assert result["sector_company_count"] == 5

    assert result["ranking_score"] == pytest.approx(
        65.92
    )

    assert result["intelligence_score"] == pytest.approx(
        75.92
    )

    assert result["assessment"] == "Good"


def test_tcs_factor_scores():
    engine = CompanyIntelligenceEngine()

    result = engine.analyse_company(
        "TCS",
        YEAR,
    )

    factors = result["factor_scores"]

    assert factors["quality"] == pytest.approx(76.92)
    assert factors["growth"] == pytest.approx(26.31)
    assert factors["profitability"] == pytest.approx(72.22)
    assert factors["financial_strength"] == pytest.approx(83.33)
    assert factors["efficiency"] == pytest.approx(90.0)


def test_tcs_strengths():
    engine = CompanyIntelligenceEngine()

    result = engine.analyse_company(
        "TCS",
        YEAR,
    )

    strengths = result["strengths"]

    assert "Strong return on equity" in strengths
    assert "Strong operating profitability" in strengths
    assert "Healthy revenue growth" in strengths
    assert "Conservative leverage" in strengths
    assert "Positive free cash flow" in strengths


def test_tcs_has_no_detected_risks():
    engine = CompanyIntelligenceEngine()

    result = engine.analyse_company(
        "TCS",
        YEAR,
    )

    assert result["risks"] == []


def test_analysis_case_insensitive():
    engine = CompanyIntelligenceEngine()

    result = engine.analyse_company(
        "tcs",
        YEAR,
    )

    assert result["company_id"] == "TCS"


def test_analysis_invalid_company():
    engine = CompanyIntelligenceEngine()

    with pytest.raises(ValueError):
        engine.analyse_company(
            "INVALID_COMPANY",
            YEAR,
        )


# =========================================================
# Summary
# =========================================================

def test_tcs_summary():
    engine = CompanyIntelligenceEngine()

    summary = engine.generate_summary(
        "TCS",
        YEAR,
    )

    assert "Tata Consultancy Services Ltd" in summary
    assert "75.92/100" in summary
    assert "classified as Good" in summary
    assert "#14 overall" in summary
    assert "#1 among 5 companies" in summary
    assert "Information Technology" in summary