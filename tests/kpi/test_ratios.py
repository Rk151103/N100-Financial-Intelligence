"""
tests/kpi/test_ratios.py

N100 Financial Intelligence Platform
Sprint 2 - Financial Ratio Engine Tests

Day 08:
- Profitability Ratios
- OPM Cross Check
- ROE
- ROCE
- ROA
"""

from src.analytics.ratios import FinancialRatioCalculator


# =========================================================
# Safe Divide
# =========================================================

def test_safe_divide():
    result = FinancialRatioCalculator.safe_divide(
        100,
        20
    )

    assert result == 5.0


def test_safe_divide_zero():
    result = FinancialRatioCalculator.safe_divide(
        100,
        0
    )

    assert result is None


# =========================================================
# Net Profit Margin
# =========================================================

def test_net_profit_margin():
    result = FinancialRatioCalculator.net_profit_margin(
        20,
        100
    )

    assert result == 20.0


def test_net_profit_margin_zero_sales():
    result = FinancialRatioCalculator.net_profit_margin(
        20,
        0
    )

    assert result is None


def test_net_profit_margin_none():
    result = FinancialRatioCalculator.net_profit_margin(
        None,
        100
    )

    assert result is None


# =========================================================
# Operating Profit Margin
# =========================================================

def test_operating_profit_margin():
    result = FinancialRatioCalculator.operating_profit_margin(
        25,
        100
    )

    assert result == 25.0


def test_operating_profit_margin_zero_sales():
    result = FinancialRatioCalculator.operating_profit_margin(
        25,
        0
    )

    assert result is None


# =========================================================
# OPM Cross Check
# =========================================================

def test_opm_cross_check_match():
    result = FinancialRatioCalculator.opm_cross_check(
        operating_profit=20,
        sales=100,
        source_opm=20
    )

    assert result["calculated_opm"] == 20.0
    assert result["difference"] == 0.0
    assert result["mismatch"] is False


def test_opm_cross_check_mismatch():
    result = FinancialRatioCalculator.opm_cross_check(
        operating_profit=20,
        sales=100,
        source_opm=10
    )

    assert result["calculated_opm"] == 20.0
    assert result["difference"] == 10.0
    assert result["mismatch"] is True


# =========================================================
# Return on Equity (ROE)
# =========================================================

def test_return_on_equity():
    result = FinancialRatioCalculator.return_on_equity(
        net_profit=20,
        equity_capital=50,
        reserves=50
    )

    assert result == 20.0


def test_return_on_equity_negative_equity():
    result = FinancialRatioCalculator.return_on_equity(
        net_profit=20,
        equity_capital=50,
        reserves=-100
    )

    assert result is None


def test_return_on_equity_zero_equity():
    result = FinancialRatioCalculator.return_on_equity(
        net_profit=20,
        equity_capital=0,
        reserves=0
    )

    assert result is None


# =========================================================
# Return on Capital Employed (ROCE)
# =========================================================

def test_return_on_capital_employed():
    result = FinancialRatioCalculator.return_on_capital_employed(
        operating_profit=20,
        other_income=10,
        equity_capital=50,
        reserves=50,
        borrowings=50
    )

    # EBIT = 20 + 10 = 30
    # Capital Employed = 50 + 50 + 50 = 150
    # ROCE = 30 / 150 * 100 = 20%

    assert result == 20.0


def test_return_on_capital_employed_invalid_capital():
    result = FinancialRatioCalculator.return_on_capital_employed(
        operating_profit=20,
        other_income=10,
        equity_capital=50,
        reserves=-100,
        borrowings=50
    )

    assert result is None


# =========================================================
# ROCE Evaluation
# =========================================================

def test_roce_non_financial_threshold():
    result = FinancialRatioCalculator.evaluate_roce(
        roce=20,
        broad_sector="Information Technology",
        absolute_threshold=15
    )

    assert result is True


def test_roce_financial_sector_benchmark():
    result = FinancialRatioCalculator.evaluate_roce(
        roce=12,
        broad_sector="Financials",
        sector_benchmark=10
    )

    assert result is True


# =========================================================
# Return on Assets (ROA)
# =========================================================

def test_return_on_assets():
    result = FinancialRatioCalculator.return_on_assets(
        net_profit=20,
        total_assets=200
    )

    assert result == 10.0


def test_return_on_assets_zero_assets():
    result = FinancialRatioCalculator.return_on_assets(
        net_profit=20,
        total_assets=0
    )

    assert result is None


# =========================================================
# Debt to Equity
# =========================================================

def test_debt_to_equity():
    result = FinancialRatioCalculator.debt_to_equity(
        borrowings=50,
        equity_capital=50,
        reserves=50
    )

    assert result == 0.5
# =========================================================
# Sprint 2 - Day 09
# Leverage & Efficiency Ratio Tests
# =========================================================
# =========================================================
# Debt-to-Equity - Debt Free
# =========================================================

def test_debt_to_equity_debt_free():
    result = FinancialRatioCalculator.debt_to_equity(
        borrowings=0,
        equity_capital=50,
        reserves=50
    )

    assert result == 0


# =========================================================
# High Leverage Flag
# =========================================================

def test_high_leverage_flag():
    result = FinancialRatioCalculator.high_leverage_flag(
        borrowings=600,
        equity_capital=50,
        reserves=50,
        broad_sector="Industrials"
    )

    assert result is True


def test_high_leverage_flag_normal():
    result = FinancialRatioCalculator.high_leverage_flag(
        borrowings=100,
        equity_capital=50,
        reserves=50,
        broad_sector="Industrials"
    )

    assert result is False


def test_high_leverage_financial_sector_exemption():
    result = FinancialRatioCalculator.high_leverage_flag(
        borrowings=1000,
        equity_capital=50,
        reserves=50,
        broad_sector="Financials"
    )

    assert result is False


# =========================================================
# Interest Coverage Ratio
# =========================================================

def test_interest_coverage():
    result = FinancialRatioCalculator.interest_coverage(
        operating_profit=100,
        other_income=20,
        interest=40
    )

    assert result == 3.0


def test_interest_coverage_zero_interest():
    result = FinancialRatioCalculator.interest_coverage(
        operating_profit=100,
        other_income=20,
        interest=0
    )

    assert result is None


# =========================================================
# Interest Coverage Label
# =========================================================

def test_interest_coverage_debt_free_label():
    result = FinancialRatioCalculator.interest_coverage_label(
        operating_profit=100,
        other_income=20,
        interest=0
    )

    assert result == "Debt Free"


def test_interest_coverage_non_debt_free_label():
    result = FinancialRatioCalculator.interest_coverage_label(
        operating_profit=100,
        other_income=20,
        interest=10
    )

    assert result is None


# =========================================================
# Interest Coverage Warning
# =========================================================

def test_interest_coverage_warning():
    result = FinancialRatioCalculator.interest_coverage_warning(
        operating_profit=10,
        other_income=0,
        interest=10
    )

    assert result is True


def test_interest_coverage_no_warning():
    result = FinancialRatioCalculator.interest_coverage_warning(
        operating_profit=30,
        other_income=0,
        interest=10
    )

    assert result is False


def test_interest_coverage_debt_free_no_warning():
    result = FinancialRatioCalculator.interest_coverage_warning(
        operating_profit=30,
        other_income=0,
        interest=0
    )

    assert result is False


# =========================================================
# Net Debt
# =========================================================

def test_net_debt():
    result = FinancialRatioCalculator.net_debt(
        borrowings=500,
        investments=200
    )

    assert result == 300


def test_net_debt_negative():
    result = FinancialRatioCalculator.net_debt(
        borrowings=100,
        investments=300
    )

    assert result == -200


# =========================================================
# Asset Turnover
# =========================================================

def test_asset_turnover():
    result = FinancialRatioCalculator.asset_turnover(
        sales=500,
        total_assets=250
    )

    assert result == 2.0


def test_asset_turnover_zero_assets():
    result = FinancialRatioCalculator.asset_turnover(
        sales=500,
        total_assets=0
    )

    assert result is None


# =========================================================
# Leverage Summary
# =========================================================

def test_leverage_summary():
    result = FinancialRatioCalculator.leverage_summary(
        borrowings=0,
        equity_capital=50,
        reserves=50,
        operating_profit=100,
        other_income=20,
        interest=0,
        investments=50,
        broad_sector="Information Technology"
    )

    assert result["debt_to_equity"] == 0
    assert result["high_leverage_flag"] is False
    assert result["interest_coverage"] is None
    assert result["icr_label"] == "Debt Free"
    assert result["icr_warning_flag"] is False
    assert result["net_debt"] == -50