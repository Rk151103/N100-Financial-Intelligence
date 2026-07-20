"""
src/analytics/ratios.py

N100 Financial Intelligence Platform
Sprint 2 - Financial Ratio Engine

Day 08 - Profitability Ratios
Day 09 - Leverage & Efficiency Ratios
"""

import sqlite3
from pathlib import Path

import pandas as pd


# =========================================================
# Project Paths
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"


class FinancialRatioCalculator:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.balance = None
        self.profit = None
        self.output = None

    # =====================================================
    # Database
    # =====================================================

    def close(self):
        """Close database connection."""

        if self.conn:
            self.conn.close()

    def load_data(self):
        """Load balance sheet and profit & loss data."""

        self.balance = pd.read_sql(
            "SELECT * FROM balancesheet",
            self.conn
        )

        self.profit = pd.read_sql(
            "SELECT * FROM profitandloss",
            self.conn
        )

        return self.balance, self.profit

    # =====================================================
    # Safe Divide
    # =====================================================

    @staticmethod
    def safe_divide(a, b):
        """Safely divide two numeric values."""

        if pd.isna(a) or pd.isna(b):
            return None

        if b == 0:
            return None

        return round(a / b, 4)

    # =====================================================
    # Day 08 - Net Profit Margin
    # =====================================================

    @classmethod
    def net_profit_margin(cls, net_profit, sales):
        """
        Net Profit Margin.

        Formula:
            net_profit / sales * 100
        """

        result = cls.safe_divide(net_profit, sales)

        if result is None:
            return None

        return round(result * 100, 4)

    # =====================================================
    # Day 08 - Operating Profit Margin
    # =====================================================

    @classmethod
    def operating_profit_margin(
        cls,
        operating_profit,
        sales
    ):
        """
        Operating Profit Margin.

        Formula:
            operating_profit / sales * 100
        """

        result = cls.safe_divide(
            operating_profit,
            sales
        )

        if result is None:
            return None

        return round(result * 100, 4)

    # =====================================================
    # Day 08 - OPM Cross Check
    # =====================================================

    @classmethod
    def opm_cross_check(
        cls,
        operating_profit,
        sales,
        source_opm
    ):
        """
        Compare calculated OPM with source OPM.

        Difference greater than 1 percentage point
        is considered a mismatch.
        """

        calculated_opm = cls.operating_profit_margin(
            operating_profit,
            sales
        )

        if (
            calculated_opm is None
            or pd.isna(source_opm)
        ):
            return {
                "calculated_opm": calculated_opm,
                "difference": None,
                "mismatch": False
            }

        difference = round(
            abs(calculated_opm - source_opm),
            4
        )

        return {
            "calculated_opm": calculated_opm,
            "difference": difference,
            "mismatch": difference > 1
        }

    # =====================================================
    # Day 08 - Return on Equity
    # =====================================================

    @classmethod
    def return_on_equity(
        cls,
        net_profit,
        equity_capital,
        reserves
    ):
        """
        Return on Equity.

        Formula:
            net_profit /
            (equity_capital + reserves) * 100

        Returns None for zero or negative equity.
        """

        if (
            pd.isna(equity_capital)
            or pd.isna(reserves)
        ):
            return None

        total_equity = (
            equity_capital + reserves
        )

        if total_equity <= 0:
            return None

        result = cls.safe_divide(
            net_profit,
            total_equity
        )

        if result is None:
            return None

        return round(result * 100, 4)

    # =====================================================
    # Day 08 - ROCE
    # =====================================================

    @classmethod
    def return_on_capital_employed(
        cls,
        operating_profit,
        other_income,
        equity_capital,
        reserves,
        borrowings
    ):
        """
        Return on Capital Employed.

        EBIT proxy:
            operating_profit + other_income

        Capital employed:
            equity_capital + reserves + borrowings
        """

        values = [
            operating_profit,
            other_income,
            equity_capital,
            reserves,
            borrowings
        ]

        if any(pd.isna(value) for value in values):
            return None

        ebit = (
            operating_profit
            + other_income
        )

        capital_employed = (
            equity_capital
            + reserves
            + borrowings
        )

        if capital_employed <= 0:
            return None

        result = cls.safe_divide(
            ebit,
            capital_employed
        )

        if result is None:
            return None

        return round(result * 100, 4)

    # =====================================================
    # Day 08 - ROCE Evaluation
    # =====================================================

    @staticmethod
    def evaluate_roce(
        roce,
        broad_sector,
        absolute_threshold=15,
        sector_benchmark=None
    ):
        """
        Evaluate ROCE.

        Financial companies use a sector-relative benchmark.
        Other companies use an absolute threshold.
        """

        if roce is None or pd.isna(roce):
            return False

        sector = str(
            broad_sector
        ).strip().lower()

        if sector == "financials":
            if (
                sector_benchmark is None
                or pd.isna(sector_benchmark)
            ):
                return False

            return roce >= sector_benchmark

        return roce >= absolute_threshold

    # =====================================================
    # Day 08 - Return on Assets
    # =====================================================

    @classmethod
    def return_on_assets(
        cls,
        net_profit,
        total_assets
    ):
        """
        Return on Assets.

        Formula:
            net_profit / total_assets * 100
        """

        result = cls.safe_divide(
            net_profit,
            total_assets
        )

        if result is None:
            return None

        return round(result * 100, 4)

    # =====================================================
    # Day 09 - Debt to Equity
    # =====================================================

    @classmethod
    def debt_to_equity(
        cls,
        borrowings,
        equity_capital,
        reserves
    ):
        """
        Debt-to-Equity Ratio.

        Formula:
            borrowings /
            (equity_capital + reserves)

        Debt-free companies return 0.
        Invalid or non-positive equity returns None.
        """

        if pd.isna(borrowings):
            return None

        if (
            pd.isna(equity_capital)
            or pd.isna(reserves)
        ):
            return None

        total_equity = (
            equity_capital + reserves
        )

        if total_equity <= 0:
            return None

        if borrowings == 0:
            return 0

        return cls.safe_divide(
            borrowings,
            total_equity
        )

    # =====================================================
    # Day 09 - High Leverage Flag
    # =====================================================

    @classmethod
    def high_leverage_flag(
        cls,
        borrowings,
        equity_capital,
        reserves,
        broad_sector
    ):
        """
        D/E > 5 is high leverage.

        Financials sector is excluded.
        """

        sector = str(
            broad_sector
        ).strip().lower()

        if sector == "financials":
            return False

        de_ratio = cls.debt_to_equity(
            borrowings,
            equity_capital,
            reserves
        )

        if de_ratio is None:
            return False

        return de_ratio > 5

    # =====================================================
    # Day 09 - Interest Coverage
    # =====================================================

    @classmethod
    def interest_coverage(
        cls,
        operating_profit,
        other_income,
        interest
    ):
        """
        Interest Coverage Ratio.

        Formula:
            (operating_profit + other_income)
            / interest

        Interest = 0 returns None.
        """

        if (
            pd.isna(operating_profit)
            or pd.isna(other_income)
            or pd.isna(interest)
        ):
            return None

        if interest == 0:
            return None

        ebit = (
            operating_profit
            + other_income
        )

        return cls.safe_divide(
            ebit,
            interest
        )

    # =====================================================
    # Day 09 - ICR Label
    # =====================================================

    @staticmethod
    def interest_coverage_label(
        operating_profit,
        other_income,
        interest
    ):
        """
        Debt-free display label.
        """

        if pd.isna(interest):
            return None

        if interest == 0:
            return "Debt Free"

        return None

    # =====================================================
    # Day 09 - ICR Warning
    # =====================================================

    @classmethod
    def interest_coverage_warning(
        cls,
        operating_profit,
        other_income,
        interest,
        threshold=1.5
    ):
        """
        ICR below 1.5 indicates interest coverage risk.

        Debt-free companies are not flagged.
        """

        icr = cls.interest_coverage(
            operating_profit,
            other_income,
            interest
        )

        if icr is None:
            return False

        return icr < threshold

    # =====================================================
    # Day 09 - Net Debt
    # =====================================================

    @staticmethod
    def net_debt(
        borrowings,
        investments
    ):
        """
        Net Debt.

        Formula:
            borrowings - investments
        """

        if (
            pd.isna(borrowings)
            or pd.isna(investments)
        ):
            return None

        return round(
            borrowings - investments,
            4
        )

    # =====================================================
    # Day 09 - Asset Turnover
    # =====================================================

    @classmethod
    def asset_turnover(
        cls,
        sales,
        total_assets
    ):
        """
        Asset Turnover.

        Formula:
            sales / total_assets
        """

        return cls.safe_divide(
            sales,
            total_assets
        )

    # =====================================================
    # Day 09 - Leverage Summary
    # =====================================================

    @classmethod
    def leverage_summary(
        cls,
        borrowings,
        equity_capital,
        reserves,
        operating_profit,
        other_income,
        interest,
        investments,
        broad_sector
    ):
        """
        Return Day 09 leverage metrics.
        """

        return {
            "debt_to_equity":
                cls.debt_to_equity(
                    borrowings,
                    equity_capital,
                    reserves
                ),

            "high_leverage_flag":
                cls.high_leverage_flag(
                    borrowings,
                    equity_capital,
                    reserves,
                    broad_sector
                ),

            "interest_coverage":
                cls.interest_coverage(
                    operating_profit,
                    other_income,
                    interest
                ),

            "icr_label":
                cls.interest_coverage_label(
                    operating_profit,
                    other_income,
                    interest
                ),

            "icr_warning_flag":
                cls.interest_coverage_warning(
                    operating_profit,
                    other_income,
                    interest
                ),

            "net_debt":
                cls.net_debt(
                    borrowings,
                    investments
                )
        }


if __name__ == "__main__":

    calculator = FinancialRatioCalculator()

    try:
        calculator.load_data()

        print(
            "Financial Ratio Calculator "
            "loaded successfully."
        )

    finally:
        calculator.close()