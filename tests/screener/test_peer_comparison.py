"""
tests/screener/test_peer_comparison.py

N100 Financial Intelligence Platform
Sprint 3 - Day 17
Peer Comparison Engine Tests
"""

import pytest

from src.screener.peer_comparison import PeerComparisonEngine


YEAR = "Mar 2024"
COMPANY = "TCS"


# =========================================================
# Initialization / Data Loading
# =========================================================

def test_engine_initialization():
    engine = PeerComparisonEngine()

    assert engine.db_path.exists()


def test_load_data():
    engine = PeerComparisonEngine()

    df = engine.load_data(YEAR)

    assert not df.empty
    assert "company_id" in df.columns
    assert "company_name" in df.columns
    assert "broad_sector" in df.columns
    assert "composite_quality_score" in df.columns


# =========================================================
# Company Lookup
# =========================================================

def test_get_company():
    engine = PeerComparisonEngine()

    company = engine.get_company(
        COMPANY,
        YEAR,
    )

    assert company["company_id"] == "TCS"
    assert company["company_name"] == "Tata Consultancy Services Ltd"
    assert company["broad_sector"] == "Information Technology"


def test_company_id_case_insensitive():
    engine = PeerComparisonEngine()

    company = engine.get_company(
        "tcs",
        YEAR,
    )

    assert company["company_id"] == "TCS"


def test_invalid_company():
    engine = PeerComparisonEngine()

    with pytest.raises(ValueError):
        engine.get_company(
            "INVALID_COMPANY",
            YEAR,
        )


# =========================================================
# Peer Detection
# =========================================================

def test_get_peers():
    engine = PeerComparisonEngine()

    peers = engine.get_peers(
        COMPANY,
        YEAR,
    )

    assert not peers.empty
    assert len(peers) == 5
    assert (
        peers["broad_sector"]
        == "Information Technology"
    ).all()


def test_peers_include_company():
    engine = PeerComparisonEngine()

    peers = engine.get_peers(
        COMPANY,
        YEAR,
        include_company=True,
    )

    assert "TCS" in peers["company_id"].values


def test_peers_exclude_company():
    engine = PeerComparisonEngine()

    peers = engine.get_peers(
        COMPANY,
        YEAR,
        include_company=False,
    )

    assert "TCS" not in peers["company_id"].values
    assert len(peers) == 4


# =========================================================
# Sector Statistics
# =========================================================

def test_sector_statistics():
    engine = PeerComparisonEngine()

    stats = engine.sector_statistics(
        COMPANY,
        YEAR,
    )

    assert not stats.empty

    assert "metric" in stats.columns
    assert "mean" in stats.columns
    assert "median" in stats.columns
    assert "minimum" in stats.columns
    assert "maximum" in stats.columns


def test_sector_statistics_contains_roe():
    engine = PeerComparisonEngine()

    stats = engine.sector_statistics(
        COMPANY,
        YEAR,
    )

    assert (
        "return_on_equity_pct"
        in stats["metric"].values
    )


# =========================================================
# Metric Ranking
# =========================================================

def test_roe_rank():
    engine = PeerComparisonEngine()

    result = engine.metric_rank(
        COMPANY,
        "return_on_equity_pct",
        YEAR,
    )

    assert result is not None
    assert result["company_id"] == "TCS"
    assert result["rank"] == 1
    assert result["peer_count"] == 5


def test_debt_to_equity_rank():
    engine = PeerComparisonEngine()

    result = engine.metric_rank(
        COMPANY,
        "debt_to_equity",
        YEAR,
    )

    assert result is not None
    assert result["rank"] >= 1
    assert result["rank"] <= result["peer_count"]


def test_invalid_metric():
    engine = PeerComparisonEngine()

    with pytest.raises(ValueError):
        engine.metric_rank(
            COMPANY,
            "invalid_metric",
            YEAR,
        )


# =========================================================
# Comparison Summary
# =========================================================

def test_comparison_summary():
    engine = PeerComparisonEngine()

    comparison = engine.comparison_summary(
        COMPANY,
        YEAR,
    )

    assert not comparison.empty

    expected_columns = {
        "metric",
        "company_value",
        "sector_median",
        "rank",
        "peer_count",
        "better_than_median",
    }

    assert expected_columns.issubset(
        comparison.columns
    )


def test_tcs_roe_better_than_sector_median():
    engine = PeerComparisonEngine()

    comparison = engine.comparison_summary(
        COMPANY,
        YEAR,
    )

    roe = comparison[
        comparison["metric"]
        == "return_on_equity_pct"
    ].iloc[0]

    assert roe["company_value"] == 50.94
    assert roe["better_than_median"]


def test_tcs_revenue_growth_below_median():
    engine = PeerComparisonEngine()

    comparison = engine.comparison_summary(
        COMPANY,
        YEAR,
    )

    revenue = comparison[
        comparison["metric"]
        == "revenue_cagr_5yr"
    ].iloc[0]

    assert revenue["company_value"] == 10.46
    assert not revenue["better_than_median"]


# =========================================================
# Quality Ranking
# =========================================================

def test_quality_ranking():
    engine = PeerComparisonEngine()

    ranking = engine.quality_ranking(
        COMPANY,
        YEAR,
    )

    assert not ranking.empty
    assert len(ranking) == 5

    assert ranking.iloc[0]["company_id"] == "LTIM"
    assert ranking.iloc[1]["company_id"] == "TCS"


def test_quality_ranking_numbers():
    engine = PeerComparisonEngine()

    ranking = engine.quality_ranking(
        COMPANY,
        YEAR,
    )

    assert ranking["rank"].tolist() == [
        1,
        2,
        3,
        4,
        5,
    ]


def test_quality_scores_sorted_descending():
    engine = PeerComparisonEngine()

    ranking = engine.quality_ranking(
        COMPANY,
        YEAR,
    )

    scores = (
        ranking["composite_quality_score"]
        .dropna()
        .tolist()
    )

    assert scores == sorted(
        scores,
        reverse=True,
    )


def test_tcs_quality_rank():
    engine = PeerComparisonEngine()

    ranking = engine.quality_ranking(
        COMPANY,
        YEAR,
    )

    tcs = ranking[
        ranking["company_id"] == "TCS"
    ].iloc[0]

    assert tcs["rank"] == 2
    assert tcs["composite_quality_score"] == pytest.approx(
        22.10
    )