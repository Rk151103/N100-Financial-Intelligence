"""
tests/screener/test_presets.py

N100 Financial Intelligence Platform
Sprint 3 - Day 16
Advanced Screener Preset Tests
"""

import pytest

from src.screener.presets import ScreenerPresets


# =========================================================
# Preset Configuration Tests
# =========================================================

def test_available_presets():
    presets = ScreenerPresets.available_presets()

    assert len(presets) == 7
    assert "high_quality" in presets
    assert "high_growth" in presets
    assert "low_debt" in presets
    assert "strong_cash_flow" in presets
    assert "efficient_business" in presets
    assert "growth_quality" in presets
    assert "conservative_quality" in presets


def test_get_high_quality_preset():
    filters = ScreenerPresets.get_preset("high_quality")

    assert filters["roe_min"] == 15
    assert filters["debt_to_equity_max"] == 1
    assert filters["opm_min"] == 10


def test_get_high_growth_preset():
    filters = ScreenerPresets.get_preset("high_growth")

    assert filters["revenue_cagr_5yr_min"] == 10
    assert filters["pat_cagr_5yr_min"] == 10
    assert filters["eps_cagr_5yr_min"] == 10


def test_get_low_debt_preset():
    filters = ScreenerPresets.get_preset("low_debt")

    assert filters["debt_to_equity_max"] == 0.5


def test_get_strong_cash_flow_preset():
    filters = ScreenerPresets.get_preset("strong_cash_flow")

    assert filters["fcf_min"] == 0
    assert filters["icr_min"] == 3


def test_get_efficient_business_preset():
    filters = ScreenerPresets.get_preset("efficient_business")

    assert filters["roe_min"] == 15
    assert filters["asset_turnover_min"] == 1


def test_get_growth_quality_preset():
    filters = ScreenerPresets.get_preset("growth_quality")

    assert filters["roe_min"] == 15
    assert filters["debt_to_equity_max"] == 1
    assert filters["revenue_cagr_5yr_min"] == 10
    assert filters["pat_cagr_5yr_min"] == 10


def test_get_conservative_quality_preset():
    filters = ScreenerPresets.get_preset("conservative_quality")

    assert filters["roe_min"] == 15
    assert filters["debt_to_equity_max"] == 0.5
    assert filters["icr_min"] == 5
    assert filters["fcf_min"] == 0


def test_invalid_preset():
    with pytest.raises(ValueError):
        ScreenerPresets.get_preset("invalid_preset")


def test_get_preset_returns_copy():
    first = ScreenerPresets.get_preset("high_quality")
    first["roe_min"] = 999

    second = ScreenerPresets.get_preset("high_quality")

    assert second["roe_min"] == 15


# =========================================================
# Real Database Tests
# =========================================================

def test_run_high_quality():
    presets = ScreenerPresets()

    result = presets.run(
        "high_quality",
        year="Mar 2024",
    )

    assert not result.empty
    assert (result["return_on_equity_pct"] >= 15).all()
    assert (result["operating_profit_margin_pct"] >= 10).all()


def test_run_high_growth():
    presets = ScreenerPresets()

    result = presets.run(
        "high_growth",
        year="Mar 2024",
    )

    assert not result.empty
    assert (result["revenue_cagr_5yr"] >= 10).all()
    assert (result["pat_cagr_5yr"] >= 10).all()
    assert (result["eps_cagr_5yr"] >= 10).all()


def test_run_efficient_business():
    presets = ScreenerPresets()

    result = presets.run(
        "efficient_business",
        year="Mar 2024",
    )

    assert not result.empty
    assert (result["return_on_equity_pct"] >= 15).all()
    assert (result["asset_turnover"] >= 1).all()


def test_run_all_presets():
    presets = ScreenerPresets()

    results = presets.run_all(
        year="Mar 2024",
    )

    assert len(results) == 7

    for preset_name in ScreenerPresets.available_presets():
        assert preset_name in results


def test_preset_summary():
    presets = ScreenerPresets()

    summary = presets.summary(
        year="Mar 2024",
    )

    assert len(summary) == 7

    for count in summary.values():
        assert isinstance(count, int)
        assert count >= 0


def test_high_quality_sorted_by_quality_score():
    presets = ScreenerPresets()

    result = presets.run(
        "high_quality",
        year="Mar 2024",
    )

    scores = (
        result["composite_quality_score"]
        .dropna()
        .tolist()
    )

    assert scores == sorted(
        scores,
        reverse=True,
    )