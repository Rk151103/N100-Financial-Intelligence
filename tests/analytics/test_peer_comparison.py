"""
tests/analytics/test_peer_comparison.py

Sprint 3 - Day 17
Peer Comparison Engine Tests
"""

from pathlib import Path

import pytest

from src.analytics.peer_comparison import PeerComparisonEngine


@pytest.fixture
def engine():
    return PeerComparisonEngine()


# =========================================================
# Database Tests
# =========================================================

def test_load_data(engine):
    df = engine.load_data("Mar 2024")

    assert not df.empty
    assert "company_name" in df.columns
    assert "broad_sector" in df.columns
    assert len(df) >= 90


# =========================================================
# Company Lookup
# =========================================================

def test_compare_icici(engine):
    peers = engine.compare("ICICI Bank Ltd")

    assert not peers.empty
    assert "company_name" in peers.columns
    assert "composite_quality_score" in peers.columns


def test_invalid_company(engine):
    with pytest.raises(ValueError):
        engine.compare("ABC XYZ Pvt Ltd")


# =========================================================
# Sector Validation
# =========================================================

def test_same_sector(engine):
    peers = engine.compare("ICICI Bank Ltd")

    sectors = peers["broad_sector"].dropna().unique()

    assert len(sectors) == 1
    assert sectors[0] == "Financials"


# =========================================================
# Ranking Tests
# =========================================================

def test_quality_rank_exists(engine):
    peers = engine.compare("ICICI Bank Ltd")

    assert "composite_quality_score_rank" in peers.columns


def test_roe_rank_exists(engine):
    peers = engine.compare("ICICI Bank Ltd")

    assert "return_on_equity_pct_rank" in peers.columns


def test_quality_sorted(engine):
    peers = engine.compare("ICICI Bank Ltd")

    scores = peers["composite_quality_score"].dropna().tolist()

    assert scores == sorted(scores, reverse=True)


# =========================================================
# CSV Export
# =========================================================

def test_export_csv(engine):

    output = engine.export_csv(
        "ICICI Bank Ltd",
        output_path="output/test_peer.csv"
    )

    assert Path(output).exists()


# =========================================================
# Data Integrity
# =========================================================

def test_peer_count(engine):

    peers = engine.compare("ICICI Bank Ltd")

    assert len(peers) >= 5


def test_required_columns(engine):

    peers = engine.compare("ICICI Bank Ltd")

    required = [
        "company_name",
        "broad_sector",
        "return_on_equity_pct",
        "operating_profit_margin_pct",
        "composite_quality_score",
    ]

    for column in required:
        assert column in peers.columns


# =========================================================
# Rank Value Tests
# =========================================================

def test_rank_values_positive(engine):

    peers = engine.compare("ICICI Bank Ltd")

    ranks = (
        peers["composite_quality_score_rank"]
        .dropna()
    )

    assert (ranks >= 1).all()


def test_top_company_rank(engine):

    peers = engine.compare("ICICI Bank Ltd")

    first_rank = peers.iloc[0][
        "composite_quality_score_rank"
    ]

    assert first_rank == 1


# =========================================================
# End-to-End
# =========================================================

def test_end_to_end(engine):

    peers = engine.compare("ICICI Bank Ltd")

    csv_path = engine.export_csv(
        "ICICI Bank Ltd",
        output_path="output/end_to_end_peer.csv"
    )

    assert not peers.empty
    assert Path(csv_path).exists()