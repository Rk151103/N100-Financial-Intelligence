"""
tests/screener/test_engine.py

N100 Financial Intelligence Platform
Sprint 3 - Day 15
Screener Engine Tests
"""

import pandas as pd

from src.screener.engine import ScreenerEngine


def create_test_dataframe():
    """Create sample financial data for screener testing."""

    return pd.DataFrame(
        [
            {
                "company_id": "TCS",
                "company_name": "TCS",
                "broad_sector": "Information Technology",
                "year": "Mar 2024",
                "return_on_equity_pct": 30.0,
                "debt_to_equity": 0.2,
                "interest_coverage": 20.0,
                "asset_turnover": 1.5,
                "free_cash_flow_cr": 1000.0,
                "operating_profit_margin_pct": 25.0,
                "revenue_cagr_5yr": 12.0,
                "pat_cagr_5yr": 15.0,
                "eps_cagr_5yr": 14.0,
                "composite_quality_score": 80.0,
                "sales": 10000.0,
                "net_profit": 2000.0,
            },
            {
                "company_id": "WEAK",
                "company_name": "Weak Company",
                "broad_sector": "Industrials",
                "year": "Mar 2024",
                "return_on_equity_pct": 10.0,
                "debt_to_equity": 2.0,
                "interest_coverage": 1.0,
                "asset_turnover": 0.5,
                "free_cash_flow_cr": -100.0,
                "operating_profit_margin_pct": 5.0,
                "revenue_cagr_5yr": 2.0,
                "pat_cagr_5yr": 1.0,
                "eps_cagr_5yr": 1.0,
                "composite_quality_score": 20.0,
                "sales": 1000.0,
                "net_profit": 50.0,
            },
            {
                "company_id": "BANK",
                "company_name": "Test Bank",
                "broad_sector": "Financials",
                "year": "Mar 2024",
                "return_on_equity_pct": 20.0,
                "debt_to_equity": 10.0,
                "interest_coverage": 5.0,
                "asset_turnover": 1.0,
                "free_cash_flow_cr": 500.0,
                "operating_profit_margin_pct": 20.0,
                "revenue_cagr_5yr": 10.0,
                "pat_cagr_5yr": 12.0,
                "eps_cagr_5yr": 11.0,
                "composite_quality_score": 60.0,
                "sales": 5000.0,
                "net_profit": 1000.0,
            },
            {
                "company_id": "DEBTFREE",
                "company_name": "Debt Free Company",
                "broad_sector": "Consumer Staples",
                "year": "Mar 2024",
                "return_on_equity_pct": 25.0,
                "debt_to_equity": 0.0,
                "interest_coverage": None,
                "asset_turnover": 2.0,
                "free_cash_flow_cr": 800.0,
                "operating_profit_margin_pct": 18.0,
                "revenue_cagr_5yr": 9.0,
                "pat_cagr_5yr": 10.0,
                "eps_cagr_5yr": 10.0,
                "composite_quality_score": 70.0,
                "sales": 8000.0,
                "net_profit": 1500.0,
            },
        ]
    )


def test_engine_initialization():
    engine = ScreenerEngine()

    assert engine.config is not None
    assert "filters" in engine.config
    assert "settings" in engine.config


def test_min_filter():
    df = create_test_dataframe()

    result = ScreenerEngine._apply_min_filter(
        df,
        "return_on_equity_pct",
        15,
    )

    assert len(result) == 3
    assert "WEAK" not in result["company_id"].values


def test_max_filter():
    df = create_test_dataframe()

    result = ScreenerEngine._apply_max_filter(
        df,
        "debt_to_equity",
        1,
    )

    assert len(result) == 2
    assert "TCS" in result["company_id"].values
    assert "DEBTFREE" in result["company_id"].values


def test_financial_sector_de_exemption():
    engine = ScreenerEngine()

    df = create_test_dataframe()

    result = engine.apply_debt_to_equity_filter(
        df,
        1,
    )

    assert "BANK" in result["company_id"].values
    assert "WEAK" not in result["company_id"].values


def test_debt_free_icr_handling():
    engine = ScreenerEngine()

    df = create_test_dataframe()

    result = engine.apply_icr_filter(
        df,
        10,
    )

    assert "TCS" in result["company_id"].values
    assert "DEBTFREE" in result["company_id"].values
    assert "WEAK" not in result["company_id"].values


def test_roe_filter():
    engine = ScreenerEngine()

    df = create_test_dataframe()

    result = engine.apply_filters(
        df,
        {
            "roe_min": 20,
        },
    )

    assert "TCS" in result["company_id"].values
    assert "BANK" in result["company_id"].values
    assert "DEBTFREE" in result["company_id"].values
    assert "WEAK" not in result["company_id"].values


def test_multiple_filters():
    engine = ScreenerEngine()

    df = create_test_dataframe()

    result = engine.apply_filters(
        df,
        {
            "roe_min": 15,
            "debt_to_equity_max": 1,
            "opm_min": 15,
            "fcf_min": 0,
        },
    )

    assert "TCS" in result["company_id"].values
    assert "BANK" in result["company_id"].values
    assert "DEBTFREE" in result["company_id"].values
    assert "WEAK" not in result["company_id"].values


def test_growth_filters():
    engine = ScreenerEngine()

    df = create_test_dataframe()

    result = engine.apply_filters(
        df,
        {
            "revenue_cagr_5yr_min": 10,
            "pat_cagr_5yr_min": 10,
            "eps_cagr_5yr_min": 10,
        },
    )

    assert "TCS" in result["company_id"].values
    assert "BANK" in result["company_id"].values
    assert "WEAK" not in result["company_id"].values


def test_asset_turnover_filter():
    engine = ScreenerEngine()

    df = create_test_dataframe()

    result = engine.apply_filters(
        df,
        {
            "asset_turnover_min": 1.5,
        },
    )

    assert "TCS" in result["company_id"].values
    assert "DEBTFREE" in result["company_id"].values
    assert "WEAK" not in result["company_id"].values


def test_sort_results():
    engine = ScreenerEngine()

    df = create_test_dataframe()

    result = engine.sort_results(df)

    assert result.iloc[0]["company_id"] == "TCS"
    assert result.iloc[-1]["company_id"] == "WEAK"


def test_real_database_load():
    engine = ScreenerEngine()

    result = engine.load_data()

    assert not result.empty
    assert "company_id" in result.columns
    assert "return_on_equity_pct" in result.columns
    assert "composite_quality_score" in result.columns


def test_real_screener_mar_2024():
    engine = ScreenerEngine()

    result = engine.screen(
        filters={
            "roe_min": 15,
            "debt_to_equity_max": 1,
        },
        year="Mar 2024",
    )

    assert not result.empty
    assert (result["return_on_equity_pct"] >= 15).all()