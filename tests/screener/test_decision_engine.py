"""
Sprint 3 - Day 21
Decision Signal Engine Tests
"""

from pathlib import Path

import pandas as pd
import pytest

from src.screener.decision_engine import DecisionSignalEngine


YEAR = "Mar 2024"

COMPANIES = [
    "TCS",
    "INFY",
    "HCLTECH",
    "LTIM",
    "RELIANCE",
    "ITC",
    "MARUTI",
    "HAL",
]


def make_analysis(
    intelligence=70,
    ranking=70,
    quality=70,
    profitability=70,
    financial_strength=70,
    growth=70,
    efficiency=70,
    risks=None,
):
    return {
        "intelligence_score": intelligence,
        "ranking_score": ranking,
        "factor_scores": {
            "quality": quality,
            "profitability": profitability,
            "financial_strength": financial_strength,
            "growth": growth,
            "efficiency": efficiency,
        },
        "risks": risks or [],
    }


# =========================================================
# Initialization
# =========================================================

def test_engine_initialization():
    engine = DecisionSignalEngine()

    assert engine.db_path.exists()
    assert engine.company_engine is not None


# =========================================================
# Helper Functions
# =========================================================

def test_safe_float():
    engine = DecisionSignalEngine()

    assert engine._safe_float("10.5") == 10.5
    assert engine._safe_float(20) == 20.0
    assert engine._safe_float(None) is None
    assert engine._safe_float("invalid") is None


def test_safe_float_nan():
    engine = DecisionSignalEngine()

    assert engine._safe_float(float("nan")) is None


def test_clamp():
    engine = DecisionSignalEngine()

    assert engine._clamp(50) == 50
    assert engine._clamp(120) == 100
    assert engine._clamp(-20) == 0


# =========================================================
# Decision Score
# =========================================================

def test_decision_score_all_equal():
    engine = DecisionSignalEngine()

    analysis = make_analysis()

    score = engine.calculate_decision_score(
        analysis
    )

    assert score == pytest.approx(70.0)


def test_decision_score_weighting():
    engine = DecisionSignalEngine()

    analysis = make_analysis(
        intelligence=80,
        ranking=60,
        quality=90,
        profitability=70,
        financial_strength=50,
        growth=40,
    )

    score = engine.calculate_decision_score(
        analysis
    )

    expected = (
        80 * 0.40
        + 60 * 0.25
        + 90 * 0.10
        + 70 * 0.10
        + 50 * 0.10
        + 40 * 0.05
    )

    assert score == pytest.approx(expected)


def test_risk_penalty():
    engine = DecisionSignalEngine()

    analysis = make_analysis(
        risks=[
            "Risk 1",
            "Risk 2",
        ]
    )

    score = engine.calculate_decision_score(
        analysis
    )

    assert score == pytest.approx(66.0)


def test_risk_penalty_capped():
    engine = DecisionSignalEngine()

    analysis = make_analysis(
        risks=[
            "1", "2", "3",
            "4", "5", "6",
        ]
    )

    score = engine.calculate_decision_score(
        analysis
    )

    assert score == pytest.approx(60.0)


def test_missing_factor_weight_renormalization():
    engine = DecisionSignalEngine()

    analysis = make_analysis(
        intelligence=80,
        ranking=60,
        quality=None,
        profitability=None,
        financial_strength=None,
        growth=None,
    )

    score = engine.calculate_decision_score(
        analysis
    )

    expected = (
        (80 * 0.40 + 60 * 0.25)
        / 0.65
    )

    assert score == pytest.approx(
        round(expected, 2)
    )


def test_all_score_data_missing():
    engine = DecisionSignalEngine()

    analysis = make_analysis(
        intelligence=None,
        ranking=None,
        quality=None,
        profitability=None,
        financial_strength=None,
        growth=None,
    )

    assert (
        engine.calculate_decision_score(
            analysis
        )
        is None
    )


def test_decision_score_upper_bound():
    engine = DecisionSignalEngine()

    analysis = make_analysis(
        intelligence=150,
        ranking=150,
        quality=150,
        profitability=150,
        financial_strength=150,
        growth=150,
    )

    assert (
        engine.calculate_decision_score(
            analysis
        )
        == 100
    )


def test_decision_score_lower_bound():
    engine = DecisionSignalEngine()

    analysis = make_analysis(
        intelligence=0,
        ranking=0,
        quality=0,
        profitability=0,
        financial_strength=0,
        growth=0,
        risks=["1", "2"],
    )

    assert (
        engine.calculate_decision_score(
            analysis
        )
        == 0
    )


# =========================================================
# Signal Classification
# =========================================================

@pytest.mark.parametrize(
    "score,expected",
    [
        (100, "Strong Candidate"),
        (80, "Strong Candidate"),
        (79.99, "Candidate"),
        (65, "Candidate"),
        (64.99, "Watch"),
        (50, "Watch"),
        (49.99, "Avoid"),
        (0, "Avoid"),
        (None, "Insufficient Data"),
    ],
)
def test_signal_classification(
    score,
    expected,
):
    assert (
        DecisionSignalEngine
        .classify_signal(score)
        == expected
    )


# =========================================================
# Confidence
# =========================================================

def test_high_confidence():
    engine = DecisionSignalEngine()

    analysis = make_analysis()

    assert (
        engine.calculate_confidence(
            analysis
        )
        == "High"
    )


def test_medium_confidence():
    engine = DecisionSignalEngine()

    analysis = make_analysis(
        growth=None,
        efficiency=None,
    )

    assert (
        engine.calculate_confidence(
            analysis
        )
        == "Medium"
    )


def test_low_confidence():
    engine = DecisionSignalEngine()

    analysis = make_analysis(
        ranking=None,
        quality=None,
        profitability=None,
        financial_strength=None,
        growth=None,
        efficiency=None,
    )

    assert (
        engine.calculate_confidence(
            analysis
        )
        == "Low"
    )


# =========================================================
# Reason Generation
# =========================================================

def test_strong_reasons():
    engine = DecisionSignalEngine()

    analysis = make_analysis(
        intelligence=90,
        ranking=85,
        quality=90,
        profitability=90,
        financial_strength=90,
        growth=90,
    )

    reasons = engine.generate_reasons(
        analysis
    )

    assert (
        "Strong overall company intelligence"
        in reasons
    )

    assert (
        "Strong multi-factor ranking score"
        in reasons
    )

    assert "Strong quality factor" in reasons
    assert "Strong profitability factor" in reasons
    assert "Strong financial strength" in reasons
    assert "Strong growth factor" in reasons


def test_weak_reasons():
    engine = DecisionSignalEngine()

    analysis = make_analysis(
        intelligence=40,
        ranking=40,
        growth=30,
    )

    reasons = engine.generate_reasons(
        analysis
    )

    assert (
        "Weak overall company intelligence"
        in reasons
    )

    assert (
        "Below-average multi-factor ranking score"
        in reasons
    )

    assert (
        "Growth factor is relatively weak"
        in reasons
    )


def test_risks_added_to_reasons():
    engine = DecisionSignalEngine()

    analysis = make_analysis(
        risks=[
            "High leverage",
            "Weak cash flow",
        ]
    )

    reasons = engine.generate_reasons(
        analysis
    )

    assert "Risk: High leverage" in reasons
    assert "Risk: Weak cash flow" in reasons


def test_max_three_risks_in_reasons():
    engine = DecisionSignalEngine()

    analysis = make_analysis(
        risks=[
            "Risk 1",
            "Risk 2",
            "Risk 3",
            "Risk 4",
        ]
    )

    reasons = engine.generate_reasons(
        analysis
    )

    risk_reasons = [
        x
        for x in reasons
        if x.startswith("Risk:")
    ]

    assert len(risk_reasons) == 3


# =========================================================
# Real Company Analysis
# =========================================================

def test_tcs_decision_analysis():
    engine = DecisionSignalEngine()

    result = engine.analyse_company(
        "TCS",
        YEAR,
    )

    assert result["company_id"] == "TCS"

    assert (
        result["company_name"]
        == "Tata Consultancy Services Ltd"
    )

    assert result[
        "decision_score"
    ] == pytest.approx(
        71.41
    )

    assert result["signal"] == "Candidate"
    assert result["confidence"] == "High"


def test_company_case_insensitive():
    engine = DecisionSignalEngine()

    result = engine.analyse_company(
        "tcs",
        YEAR,
    )

    assert result["company_id"] == "TCS"


def test_invalid_company():
    engine = DecisionSignalEngine()

    with pytest.raises(ValueError):
        engine.analyse_company(
            "INVALID_COMPANY",
            YEAR,
        )


def test_hal_strong_candidate():
    engine = DecisionSignalEngine()

    result = engine.analyse_company(
        "HAL",
        YEAR,
    )

    assert result[
        "decision_score"
    ] == pytest.approx(
        82.84
    )

    assert (
        result["signal"]
        == "Strong Candidate"
    )


def test_reliance_avoid():
    engine = DecisionSignalEngine()

    result = engine.analyse_company(
        "RELIANCE",
        YEAR,
    )

    assert result[
        "decision_score"
    ] == pytest.approx(
        35.12
    )

    assert result["signal"] == "Avoid"


# =========================================================
# Multiple Company Analysis
# =========================================================

def test_analyse_companies():
    engine = DecisionSignalEngine()

    df = engine.analyse_companies(
        COMPANIES,
        YEAR,
    )

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 8


def test_decision_ranking_sorted():
    engine = DecisionSignalEngine()

    df = engine.analyse_companies(
        COMPANIES,
        YEAR,
    )

    scores = df[
        "decision_score"
    ].tolist()

    assert scores == sorted(
        scores,
        reverse=True,
    )


def test_decision_rank_sequence():
    engine = DecisionSignalEngine()

    df = engine.analyse_companies(
        COMPANIES,
        YEAR,
    )

    assert (
        df["decision_rank"].tolist()
        == list(range(1, 9))
    )


def test_hal_rank_one():
    engine = DecisionSignalEngine()

    df = engine.analyse_companies(
        COMPANIES,
        YEAR,
    )

    assert (
        df.iloc[0]["company_id"]
        == "HAL"
    )


def test_duplicate_companies_removed():
    engine = DecisionSignalEngine()

    df = engine.analyse_companies(
        [
            "TCS",
            "tcs",
            "INFY",
            "INFY",
        ],
        YEAR,
    )

    assert len(df) == 2


def test_none_company_list():
    engine = DecisionSignalEngine()

    with pytest.raises(ValueError):
        engine.analyse_companies(
            None,
            YEAR,
        )


def test_empty_company_list():
    engine = DecisionSignalEngine()

    with pytest.raises(ValueError):
        engine.analyse_companies(
            [],
            YEAR,
        )


def test_ignore_invalid_company():
    engine = DecisionSignalEngine()

    df = engine.analyse_companies(
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


def test_all_invalid_rejected():
    engine = DecisionSignalEngine()

    with pytest.raises(ValueError):
        engine.analyse_companies(
            [
                "INVALID_ONE",
                "INVALID_TWO",
            ],
            YEAR,
            ignore_invalid=True,
        )


# =========================================================
# Signal Distribution
# =========================================================

def test_signal_distribution():
    engine = DecisionSignalEngine()

    result = engine.signal_distribution(
        COMPANIES,
        YEAR,
    )

    assert (
        result["company_count"].sum()
        == 8
    )

    assert (
        result["weight_pct"].sum()
        == pytest.approx(100.0)
    )


def test_candidate_distribution():
    engine = DecisionSignalEngine()

    result = engine.signal_distribution(
        COMPANIES,
        YEAR,
    )

    row = result[
        result["signal"]
        == "Candidate"
    ].iloc[0]

    assert row["company_count"] == 4

    assert row[
        "weight_pct"
    ] == pytest.approx(
        50.0
    )


# =========================================================
# CSV Export
# =========================================================

def test_export_csv(tmp_path):
    engine = DecisionSignalEngine()

    output_file = (
        tmp_path
        / "decision_signals_test.csv"
    )

    result = engine.export_csv(
        COMPANIES,
        YEAR,
        output_path=output_file,
    )

    assert isinstance(result, Path)
    assert result.exists()

    df = pd.read_csv(result)

    assert len(df) == 8

    assert "decision_score" in df.columns
    assert "signal" in df.columns
    assert "confidence" in df.columns

    assert (
        df.iloc[0]["company_id"]
        == "HAL"
    )