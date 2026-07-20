"""
src/analytics/ratios.py

Financial Ratio Calculator

N100 Financial Intelligence Platform
"""

import sqlite3
from pathlib import Path

import pandas as pd


# -------------------------------------------------------
# Project Paths
# -------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"


class FinancialRatioCalculator:

    def __init__(self):

        self.conn = sqlite3.connect(DB_PATH)

        self.balance = None
        self.profit = None
        self.output = None

    # ---------------------------------------------------
    # Load Data
    # ---------------------------------------------------

    def load_data(self):

        """
        Load required financial tables from SQLite.
        """

        self.balance = pd.read_sql(
            """
            SELECT *
            FROM balancesheet
            """,
            self.conn
        )

        self.profit = pd.read_sql(
            """
            SELECT *
            FROM profitandloss
            """,
            self.conn
        )

        print("\nBalance Sheet")
        print(self.balance.head())

        print("\nProfit & Loss")
        print(self.profit.head())

    # ---------------------------------------------------
    # Safe Division
    # ---------------------------------------------------

    @staticmethod
    def safe_divide(a, b):

        """
        Safely divide two numbers.

        Returns None when:
        - numerator is NULL/NaN
        - denominator is NULL/NaN
        - denominator is zero
        """

        if pd.isna(a):
            return None

        if pd.isna(b):
            return None

        if b == 0:
            return None

        return round(a / b, 4)

    # ---------------------------------------------------
    # Net Profit Margin
    # ---------------------------------------------------

    @staticmethod
    def net_profit_margin(net_profit, sales):

        ratio = FinancialRatioCalculator.safe_divide(
            net_profit,
            sales
        )

        if ratio is None:
            return None

        return round(ratio * 100, 2)

    # ---------------------------------------------------
    # Operating Profit Margin
    # ---------------------------------------------------

    @staticmethod
    def operating_profit_margin(
        operating_profit,
        sales
    ):

        ratio = FinancialRatioCalculator.safe_divide(
            operating_profit,
            sales
        )

        if ratio is None:
            return None

        return round(ratio * 100, 2)

    # ---------------------------------------------------
    # Return on Equity
    # ---------------------------------------------------

    @staticmethod
    def return_on_equity(
        net_profit,
        equity_capital,
        reserves
    ):

        total_equity = (
            equity_capital + reserves
        )

        ratio = FinancialRatioCalculator.safe_divide(
            net_profit,
            total_equity
        )

        if ratio is None:
            return None

        return round(ratio * 100, 2)

    # ---------------------------------------------------
    # Debt to Equity
    # ---------------------------------------------------

    @staticmethod
    def debt_to_equity(
        borrowings,
        equity_capital,
        reserves
    ):

        total_equity = (
            equity_capital + reserves
        )

        return FinancialRatioCalculator.safe_divide(
            borrowings,
            total_equity
        )

    # ---------------------------------------------------
    # Calculate Ratios
    # ---------------------------------------------------

    def calculate(self):

        if self.balance is None or self.profit is None:
            self.load_data()

        merged = pd.merge(
            self.profit,
            self.balance,
            on=["company_id", "year"],
            how="inner"
        )

        merged["net_profit_margin_pct"] = merged.apply(
            lambda row:
            self.net_profit_margin(
                row["net_profit"],
                row["sales"]
            ),
            axis=1
        )

        merged["operating_profit_margin_pct"] = merged.apply(
            lambda row:
            self.operating_profit_margin(
                row["operating_profit"],
                row["sales"]
            ),
            axis=1
        )

        merged["return_on_equity_pct"] = merged.apply(
            lambda row:
            self.return_on_equity(
                row["net_profit"],
                row["equity_capital"],
                row["reserves"]
            ),
            axis=1
        )

        merged["debt_to_equity"] = merged.apply(
            lambda row:
            self.debt_to_equity(
                row["borrowings"],
                row["equity_capital"],
                row["reserves"]
            ),
            axis=1
        )

        self.output = merged

        return self.output

    # ---------------------------------------------------
    # Close Database
    # ---------------------------------------------------

    def close(self):

        if self.conn:
            self.conn.close()


# -------------------------------------------------------
# Main
# -------------------------------------------------------

def main():

    calculator = FinancialRatioCalculator()

    try:

        result = calculator.calculate()

        print("\nCalculated Financial Ratios\n")

        columns = [
            "company_id",
            "year",
            "net_profit_margin_pct",
            "operating_profit_margin_pct",
            "return_on_equity_pct",
            "debt_to_equity"
        ]

        print(
            result[
                columns
            ].head(20)
        )

    finally:

        calculator.close()


if __name__ == "__main__":

    main()