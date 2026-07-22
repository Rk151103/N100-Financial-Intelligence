"""
tests/screener/test_ranking.py

N100 Financial Intelligence Platform
Sprint 3 - Day 18
Multi-Factor Ranking Engine Tests
"""

import pandas as pd
import pytest

from src.screener.ranking import RankingEngine


YEAR = "Mar 2024"


# =========================================================
# Initialization / Weight Validation
# =========================================================

def test_engine_initialization():
    engine = RankingEngine()

    assert engine.db_path.exists()
    assert sum(engine.weights.values()) == pytest.approx(1.0)


def test_custom_weights():
    weights = {
        "quality": 0.30,
        "growth": 0.20,
        "profitability": 0.20,
        "financial_strength": 0.20,
        "efficiency": 0.10,
    }

    engine = RankingEngine(weights=weights)

    assert engine.weights == weights


def test_invalid_weight_total():
    weights = {
        "quality": 0.50,
        "growth": 0.30,
        "profitability": 0.20,
        "financial_strength": 0.20,
        "efficiency": 0.10,
    }

    with pytest.raises(ValueError):
        RankingEngine(weights=weights)


def test_negative_weight():
    weights = {
        "quality": 0.30,
        "growth": 0.30,
        "profitability": 0.20,
        "financial_strength": 0.30,
        "efficiency": -0.10,
    }

    with pytest.raises(ValueError):
        RankingEngine(weights=weights)


def test_missing_weight():
    weights = {
        "quality": 0.30,
        "growth": 0.25,
        "profitability": 0.20,
        "financial_strength": 0.25,
    }

    with pytest.raises(ValueError):
        RankingEngine(weights=weights)


# =========================================================
# Percentile Scoring
# =========================================================

def test_percentile_higher_is_better():
    series = pd.Series([10, 20, 30])

    result = RankingEngine.percentile_score(
        series,
        higher_is_better=True,
    )

    assert result.iloc[2] > result.iloc[1]
    assert result.iloc[1] > result.iloc[0]


def test_percentile_lower_is_better():
    series = pd.Series([1, 2, 3])

    result = RankingEngine.percentile_score(
        series,
        higher_is_better=False,
    )

    assert result.iloc[0] > result.iloc[1]
    assert result.iloc[1] > result.iloc[2]


def test_percentile_missing_value():
    series = pd.Series([10, None, 30])

    result = RankingEngine.percentile_score(series)

    assert pd.isna(result.iloc[1])


# =========================================================
# Database Loading
# =========================================================

def test_load_real_data():
    engine = RankingEngine()

    df = engine.load_data(YEAR)

    assert not df.empty
    assert len(df) == 91

    required = {
        "company_id",
        "company_name",
        "broad_sector",
        "return_on_equity_pct",
        "debt_to_equity",
        "composite_quality_score",
    }

    assert required.issubset(df.columns)


# =========================================================
# Factor Scores
# =========================================================

def test_factor_scores_created():
    engine = RankingEngine()

    df = engine.load_data(YEAR)
    result = engine.calculate_factor_scores(df)

    expected = {
        "quality_score",
        "growth_score",
        "profitability_score",
        "financial_strength_score",
        "efficiency_score",
    }

    assert expected.issubset(result.columns)


def test_factor_scores_in_valid_range():
    engine = RankingEngine()

    df = engine.load_data(YEAR)
    result = engine.calculate_factor_scores(df)

    score_columns = [
        "quality_score",
        "growth_score",
        "profitability_score",
        "financial_strength_score",
        "efficiency_score",
    ]

    for column in score_columns:
        values = result[column].dropna()

        assert (values >= 0).all()
        assert (values <= 100).all()


# =========================================================
# Final Score
# =========================================================

def test_final_score_created():
    engine = RankingEngine()

    df = engine.load_data(YEAR)
    result = engine.calculate_final_score(df)

    assert "final_score" in result.columns
    assert result["final_score"].notna().any()


def test_final_score_valid_range():
    engine = RankingEngine()

    df = engine.load_data(YEAR)
    result = engine.calculate_final_score(df)

    values = result["final_score"].dropna()

    assert (values >= 0).all()
    assert (values <= 100).all()


def test_missing_factor_weight_renormalization():
    engine = RankingEngine()

    df = pd.DataFrame(
        {
            "company_id": ["TEST"],
            "company_name": ["Test Ltd"],
            "broad_sector": ["Test"],
            "year": [YEAR],
            "return_on_equity_pct": [20],
            "debt_to_equity": [0.5],
            "interest_coverage": [5],
            "asset_turnover": [1.5],
            "free_cash_flow_cr": [100],
            "operating_profit_margin_pct": [15],
            "revenue_cagr_5yr": [None],
            "pat_cagr_5yr": [None],
            "eps_cagr_5yr": [None],
            "composite_quality_score": [50],
        }
    )

    result = engine.calculate_final_score(df)

    assert pd.notna(result.iloc[0]["final_score"])


# =========================================================
# Overall Ranking
# =========================================================

def test_rank_companies():
    engine = RankingEngine()

    ranking = engine.rank_companies(YEAR)

    assert not ranking.empty
    assert len(ranking) == 91
    assert ranking.iloc[0]["rank"] == 1


def test_ranking_sorted_descending():
    engine = RankingEngine()

    ranking = engine.rank_companies(YEAR)

    scores = (
        ranking["final_score"]
        .dropna()
        .tolist()
    )

    assert scores == sorted(
        scores,
        reverse=True,
    )


def test_top_n():
    engine = RankingEngine()

    ranking = engine.rank_companies(
        year=YEAR,
        top_n=10,
    )

    assert len(ranking) == 10
    assert ranking["rank"].tolist() == list(
        range(1, 11)
    )


def test_indigo_rank_one():
    engine = RankingEngine()

    ranking = engine.rank_companies(YEAR)

    assert ranking.iloc[0]["company_id"] == "INDIGO"
    assert ranking.iloc[0]["final_score"] == pytest.approx(
        91.59
    )


# =========================================================
# Company Ranking
# =========================================================

def test_get_tcs_rank():
    engine = RankingEngine()

    result = engine.get_company_rank(
        "TCS",
        YEAR,
    )

    assert result["company_id"] == "TCS"
    assert result["rank"] == 14
    assert result["final_score"] == pytest.approx(
        65.92
    )


def test_company_rank_case_insensitive():
    engine = RankingEngine()

    result = engine.get_company_rank(
        "tcs",
        YEAR,
    )

    assert result["company_id"] == "TCS"


def test_invalid_company():
    engine = RankingEngine()

    with pytest.raises(ValueError):
        engine.get_company_rank(
            "INVALID_COMPANY",
            YEAR,
        )


# =========================================================
# Sector Ranking
# =========================================================

def test_tcs_sector_rank():
    engine = RankingEngine()

    result = engine.sector_rank(
        "TCS",
        YEAR,
    )

    assert result["company_id"] == "TCS"
    assert result["sector"] == "Information Technology"
    assert result["sector_rank"] == 1
    assert result["sector_company_count"] == 5


def test_sector_ranking():
    engine = RankingEngine()

    ranking = engine.rank_companies(
        year=YEAR,
        sector="Information Technology",
    )

    assert len(ranking) == 5

    assert (
        ranking["broad_sector"]
        == "Information Technology"
    ).all()

    assert ranking["rank"].tolist() == [
        1,
        2,
        3,
        4,
        5,
    ]


def test_unknown_sector_returns_empty():
    engine = RankingEngine()

    ranking = engine.rank_companies(
        year=YEAR,
        sector="Unknown Sector",
    )

    assert ranking.empty