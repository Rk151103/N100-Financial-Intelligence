"""
tests/kpi/test_cagr.py

N100 Financial Intelligence Platform
Sprint 2 - Day 10

CAGR Engine Tests
"""

from src.analytics.cagr import CAGREngine, calculate_cagr


# =========================================================
# Existing / Core CAGR Tests
# =========================================================

def test_cagr_calculation():
    result = calculate_cagr(
        100,
        200,
        5
    )

    assert result == 14.87


def test_cagr_no_growth():
    result = calculate_cagr(
        100,
        100,
        5
    )

    assert result == 0.0


def test_cagr_invalid_beginning_value():
    result = calculate_cagr(
        0,
        200,
        5
    )

    assert result is None


def test_cagr_invalid_years():
    result = calculate_cagr(
        100,
        200,
        0
    )

    assert result is None


def test_cagr_none_value():
    result = calculate_cagr(
        None,
        200,
        5
    )

    assert result is None


# =========================================================
# Day 10 - Normal CAGR With Flag
# =========================================================

def test_cagr_normal_flag():
    result = CAGREngine.calculate_with_flag(
        beginning_value=100,
        ending_value=200,
        years=5
    )

    assert result["value"] == 14.87
    assert result["flag"] == "NORMAL"


# =========================================================
# DECLINE_TO_LOSS
# Positive Beginning -> Negative Ending
# =========================================================

def test_cagr_decline_to_loss():
    result = CAGREngine.calculate_with_flag(
        beginning_value=100,
        ending_value=-50,
        years=5
    )

    assert result["value"] is None
    assert result["flag"] == "DECLINE_TO_LOSS"


# =========================================================
# TURNAROUND
# Negative Beginning -> Positive Ending
# =========================================================

def test_cagr_turnaround():
    result = CAGREngine.calculate_with_flag(
        beginning_value=-100,
        ending_value=200,
        years=5
    )

    assert result["value"] is None
    assert result["flag"] == "TURNAROUND"


# =========================================================
# BOTH_NEGATIVE
# =========================================================

def test_cagr_both_negative():
    result = CAGREngine.calculate_with_flag(
        beginning_value=-100,
        ending_value=-50,
        years=5
    )

    assert result["value"] is None
    assert result["flag"] == "BOTH_NEGATIVE"


# =========================================================
# ZERO_BASE
# =========================================================

def test_cagr_zero_base():
    result = CAGREngine.calculate_with_flag(
        beginning_value=0,
        ending_value=100,
        years=5
    )

    assert result["value"] is None
    assert result["flag"] == "ZERO_BASE"


# =========================================================
# INSUFFICIENT DATA
# =========================================================

def test_cagr_insufficient_data():
    result = CAGREngine.calculate_with_flag(
        beginning_value=100,
        ending_value=200,
        years=5,
        available_years=3
    )

    assert result["value"] is None
    assert result["flag"] == "INSUFFICIENT"


def test_cagr_none_is_insufficient():
    result = CAGREngine.calculate_with_flag(
        beginning_value=None,
        ending_value=200,
        years=5
    )

    assert result["value"] is None
    assert result["flag"] == "INSUFFICIENT"


# =========================================================
# Revenue CAGR
# =========================================================

def test_revenue_cagr():
    result = CAGREngine.revenue_cagr(
        beginning_sales=100,
        ending_sales=200,
        years=5,
        available_years=5
    )

    assert result["value"] == 14.87
    assert result["flag"] == "NORMAL"


def test_revenue_cagr_insufficient():
    result = CAGREngine.revenue_cagr(
        beginning_sales=100,
        ending_sales=200,
        years=10,
        available_years=5
    )

    assert result["value"] is None
    assert result["flag"] == "INSUFFICIENT"


# =========================================================
# PAT CAGR
# =========================================================

def test_pat_cagr():
    result = CAGREngine.pat_cagr(
        beginning_pat=100,
        ending_pat=200,
        years=5,
        available_years=5
    )

    assert result["value"] == 14.87
    assert result["flag"] == "NORMAL"


def test_pat_cagr_turnaround():
    result = CAGREngine.pat_cagr(
        beginning_pat=-100,
        ending_pat=200,
        years=5,
        available_years=5
    )

    assert result["value"] is None
    assert result["flag"] == "TURNAROUND"


# =========================================================
# EPS CAGR
# =========================================================

def test_eps_cagr():
    result = CAGREngine.eps_cagr(
        beginning_eps=10,
        ending_eps=20,
        years=5,
        available_years=5
    )

    assert result["value"] == 14.87
    assert result["flag"] == "NORMAL"


def test_eps_cagr_decline_to_loss():
    result = CAGREngine.eps_cagr(
        beginning_eps=10,
        ending_eps=-5,
        years=5,
        available_years=5
    )

    assert result["value"] is None
    assert result["flag"] == "DECLINE_TO_LOSS"


# =========================================================
# Standard Growth Windows
# =========================================================

def test_growth_windows_all_available():
    result = CAGREngine.calculate_growth_windows(
        beginning_value=100,
        ending_value=200,
        available_years=10
    )

    assert result["cagr_3yr"] is not None
    assert result["cagr_3yr_flag"] == "NORMAL"

    assert result["cagr_5yr"] is not None
    assert result["cagr_5yr_flag"] == "NORMAL"

    assert result["cagr_10yr"] is not None
    assert result["cagr_10yr_flag"] == "NORMAL"


def test_growth_windows_insufficient_for_10_year():
    result = CAGREngine.calculate_growth_windows(
        beginning_value=100,
        ending_value=200,
        available_years=5
    )

    assert result["cagr_3yr_flag"] == "NORMAL"
    assert result["cagr_5yr_flag"] == "NORMAL"

    assert result["cagr_10yr"] is None
    assert result["cagr_10yr_flag"] == "INSUFFICIENT"


# =========================================================
# Invalid Years
# =========================================================

def test_cagr_with_flag_invalid_years():
    result = CAGREngine.calculate_with_flag(
        beginning_value=100,
        ending_value=200,
        years=0
    )

    assert result["value"] is None
    assert result["flag"] == "INSUFFICIENT"