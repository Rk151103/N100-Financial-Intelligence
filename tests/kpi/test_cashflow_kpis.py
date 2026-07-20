"""
tests/kpi/test_cashflow_kpis.py

N100 Financial Intelligence Platform
Sprint 2 - Day 11

Cash Flow KPI & Capital Allocation Tests
"""

from src.analytics.cashflow_kpis import CashFlowKPI


# =========================================================
# Free Cash Flow
# =========================================================

def test_free_cash_flow():
    result = CashFlowKPI.free_cash_flow(
        operating_activity=150,
        investing_activity=-50
    )

    assert result == 100


def test_free_cash_flow_negative():
    result = CashFlowKPI.free_cash_flow(
        operating_activity=50,
        investing_activity=-100
    )

    assert result == -50


def test_free_cash_flow_missing():
    result = CashFlowKPI.free_cash_flow(
        operating_activity=None,
        investing_activity=-50
    )

    assert result is None


# =========================================================
# CFO / PAT Ratio
# =========================================================

def test_cfo_pat_ratio():
    result = CashFlowKPI.cfo_pat_ratio(
        operating_activity=150,
        net_profit=100
    )

    assert result == 1.5


def test_cfo_pat_ratio_zero_pat():
    result = CashFlowKPI.cfo_pat_ratio(
        operating_activity=150,
        net_profit=0
    )

    assert result is None


# =========================================================
# CFO Quality Labels
# =========================================================

def test_cfo_quality_high():
    assert (
        CashFlowKPI.cfo_quality_label(1.5)
        == "High Quality"
    )


def test_cfo_quality_moderate():
    assert (
        CashFlowKPI.cfo_quality_label(0.75)
        == "Moderate"
    )


def test_cfo_quality_accrual_risk():
    assert (
        CashFlowKPI.cfo_quality_label(0.3)
        == "Accrual Risk"
    )


# =========================================================
# 5-Year CFO Quality
# =========================================================

def test_cfo_quality_score_5yr():
    result = CashFlowKPI.cfo_quality_score_5yr(
        operating_activities=[
            120,
            130,
            140,
            150,
            160
        ],
        net_profits=[
            100,
            100,
            100,
            100,
            100
        ]
    )

    assert result["ratio"] == 1.4
    assert result["label"] == "High Quality"


# =========================================================
# CapEx Intensity
# =========================================================

def test_capex_intensity_asset_light():
    result = CashFlowKPI.capex_intensity(
        investing_activity=-20,
        sales=1000
    )

    assert result["value"] == 2.0
    assert result["label"] == "Asset Light"


def test_capex_intensity_moderate():
    result = CashFlowKPI.capex_intensity(
        investing_activity=-50,
        sales=1000
    )

    assert result["value"] == 5.0
    assert result["label"] == "Moderate"


def test_capex_intensity_capital_intensive():
    result = CashFlowKPI.capex_intensity(
        investing_activity=-100,
        sales=1000
    )

    assert result["value"] == 10.0
    assert result["label"] == "Capital Intensive"


def test_capex_intensity_zero_sales():
    result = CashFlowKPI.capex_intensity(
        investing_activity=-100,
        sales=0
    )

    assert result["value"] is None
    assert result["label"] is None


# =========================================================
# FCF Conversion Rate
# =========================================================

def test_fcf_conversion_rate():
    result = CashFlowKPI.fcf_conversion_rate(
        operating_activity=150,
        investing_activity=-50,
        operating_profit=200
    )

    assert result == 50.0


def test_fcf_conversion_zero_operating_profit():
    result = CashFlowKPI.fcf_conversion_rate(
        operating_activity=150,
        investing_activity=-50,
        operating_profit=0
    )

    assert result is None


# =========================================================
# Capital Allocation Patterns
# =========================================================

def test_pattern_reinvestor():
    result = CashFlowKPI.capital_allocation_pattern(
        100,
        -50,
        -20,
        cfo_pat_ratio=0.8
    )

    assert result == "Reinvestor"


def test_pattern_shareholder_returns():
    result = CashFlowKPI.capital_allocation_pattern(
        150,
        -50,
        -20,
        cfo_pat_ratio=1.5
    )

    assert result == "Shareholder Returns"


def test_pattern_liquidating_assets():
    result = CashFlowKPI.capital_allocation_pattern(
        100,
        50,
        -20
    )

    assert result == "Liquidating Assets"


def test_pattern_distress_signal():
    result = CashFlowKPI.capital_allocation_pattern(
        -100,
        50,
        20
    )

    assert result == "Distress Signal"


def test_pattern_growth_funded_by_debt():
    result = CashFlowKPI.capital_allocation_pattern(
        -100,
        -50,
        20
    )

    assert result == "Growth Funded by Debt"


def test_pattern_cash_accumulator():
    result = CashFlowKPI.capital_allocation_pattern(
        100,
        50,
        20
    )

    assert result == "Cash Accumulator"


def test_pattern_pre_revenue():
    result = CashFlowKPI.capital_allocation_pattern(
        -100,
        -50,
        -20
    )

    assert result == "Pre-Revenue"


def test_pattern_mixed():
    result = CashFlowKPI.capital_allocation_pattern(
        100,
        -50,
        20
    )

    assert result == "Mixed"


# =========================================================
# Complete Summary
# =========================================================

def test_calculate_summary():
    result = CashFlowKPI.calculate_summary(
        operating_activity=150,
        investing_activity=-50,
        financing_activity=-30,
        net_profit=100,
        sales=1000,
        operating_profit=200
    )

    assert result["free_cash_flow"] == 100
    assert result["cfo_pat_ratio"] == 1.5
    assert result["cfo_quality_label"] == "High Quality"

    assert result["capex_intensity_pct"] == 5.0
    assert result["capex_intensity_label"] == "Moderate"

    assert result["fcf_conversion_rate_pct"] == 50.0

    assert result["cfo_sign"] == "+"
    assert result["cfi_sign"] == "-"
    assert result["cff_sign"] == "-"

    assert result["pattern_label"] == "Shareholder Returns"