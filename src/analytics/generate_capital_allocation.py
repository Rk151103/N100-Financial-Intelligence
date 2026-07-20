"""
Generate Capital Allocation Report
N100 Financial Intelligence Platform
Sprint 2 - Day 11
"""

import sqlite3
from pathlib import Path

import pandas as pd

from src.analytics.cashflow_kpis import CashFlowKPI


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_FILE = OUTPUT_DIR / "capital_allocation.csv"


def generate_capital_allocation():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    conn = sqlite3.connect(DB_PATH)

    try:

        query = """
        SELECT
            company_id,
            year,
            operating_activity,
            investing_activity,
            financing_activity
        FROM cashflow
        ORDER BY company_id, year
        """

        df = pd.read_sql_query(
            query,
            conn
        )

        if df.empty:
            print("No cash flow data found.")
            return

        # Calculate cash-flow signs
        df["cfo_sign"] = df[
            "operating_activity"
        ].apply(
            CashFlowKPI.cashflow_sign
        )

        df["cfi_sign"] = df[
            "investing_activity"
        ].apply(
            CashFlowKPI.cashflow_sign
        )

        df["cff_sign"] = df[
            "financing_activity"
        ].apply(
            CashFlowKPI.cashflow_sign
        )

        # Classify capital allocation pattern
        df["pattern_label"] = df.apply(
            lambda row:
            CashFlowKPI.capital_allocation_pattern(
                row["operating_activity"],
                row["investing_activity"],
                row["financing_activity"]
            ),
            axis=1
        )

        # Required Sprint 2 output columns
        output_df = df[
            [
                "company_id",
                "year",
                "cfo_sign",
                "cfi_sign",
                "cff_sign",
                "pattern_label"
            ]
        ]

        output_df.to_csv(
            OUTPUT_FILE,
            index=False
        )

        print(
            "\nCapital Allocation Report Generated"
        )

        print(
            f"Rows: {len(output_df)}"
        )

        print(
            f"Output: {OUTPUT_FILE}"
        )

        print(
            "\nPattern Distribution:"
        )

        print(
            output_df[
                "pattern_label"
            ].value_counts()
        )

    finally:

        conn.close()


if __name__ == "__main__":

    generate_capital_allocation()