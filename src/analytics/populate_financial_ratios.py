"""
src/analytics/populate_financial_ratios.py

N100 Financial Intelligence Platform
Sprint 2 - Day 12

Populate Financial Ratios Table
"""

import sqlite3
from pathlib import Path

import pandas as pd

from src.analytics.ratios import FinancialRatioCalculator
from src.analytics.cashflow_kpis import CashFlowKPI
from src.analytics.cagr import CAGREngine


# =========================================================
# Project Paths
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"


# =========================================================
# Missing Columns
# =========================================================

NEW_COLUMNS = {
    "revenue_cagr_5yr": "REAL",
    "pat_cagr_5yr": "REAL",
    "eps_cagr_5yr": "REAL",
    "composite_quality_score": "REAL",
}


def safe_value(value):
    """
    Convert pandas NaN to None for SQLite.
    """

    if value is None:
        return None

    if pd.isna(value):
        return None

    return value


# =========================================================
# Ensure Schema
# =========================================================

def ensure_columns(conn):

    existing = {
        row[1]
        for row in conn.execute(
            "PRAGMA table_info(financial_ratios)"
        ).fetchall()
    }

    for column, data_type in NEW_COLUMNS.items():

        if column not in existing:

            print(
                f"Adding column: {column}"
            )

            conn.execute(
                f"""
                ALTER TABLE financial_ratios
                ADD COLUMN {column} {data_type}
                """
            )

    conn.commit()


# =========================================================
# Load Source Data
# =========================================================

def load_data(conn):

    print("\nLoading source data...")

    profit = pd.read_sql_query(
        """
        SELECT *
        FROM profitandloss
        """,
        conn
    )

    balance = pd.read_sql_query(
        """
        SELECT *
        FROM balancesheet
        """,
        conn
    )

    cashflow = pd.read_sql_query(
        """
        SELECT *
        FROM cashflow
        """,
        conn
    )

    print(
        f"Profit & Loss : {len(profit)}"
    )

    print(
        f"Balance Sheet : {len(balance)}"
    )

    print(
        f"Cash Flow     : {len(cashflow)}"
    )

    return profit, balance, cashflow


# =========================================================
# Merge Data
# =========================================================

def merge_data(
    profit,
    balance,
    cashflow
):

    print("\nMerging company-year datasets...")

    # P&L is the base universe.
    # Expected target: 1,164 company-year rows.

    df = profit.merge(
        balance,
        on=[
            "company_id",
            "year"
        ],
        how="left",
        suffixes=(
            "",
            "_balance"
        )
    )

    df = df.merge(
        cashflow,
        on=[
            "company_id",
            "year"
        ],
        how="left",
        suffixes=(
            "",
            "_cashflow"
        )
    )

    print(
        f"Merged rows: {len(df)}"
    )

    return df


# =========================================================
# CAGR Helper
# =========================================================

def calculate_company_cagr(
    company_df,
    value_column,
    current_index,
    window=5
):
    """
    Calculate CAGR using the value approximately
    5 observations earlier for the same company.

    Returns None when historical data is insufficient
    or CAGR edge-case rules prevent calculation.
    """

    if current_index < window:
        return None

    beginning_value = company_df.iloc[
        current_index - window
    ][value_column]

    ending_value = company_df.iloc[
        current_index
    ][value_column]

    result = CAGREngine.calculate_with_flag(
        beginning_value=beginning_value,
        ending_value=ending_value,
        years=window,
        available_years=window
    )

    return result["value"]


# =========================================================
# Calculate CAGR Columns
# =========================================================

def add_cagr_columns(df):

    print("\nCalculating 5-year CAGR metrics...")

    df[
        "revenue_cagr_5yr"
    ] = None

    df[
        "pat_cagr_5yr"
    ] = None

    df[
        "eps_cagr_5yr"
    ] = None

    # Keep original row positions
    df = df.reset_index(
        drop=True
    )

    for company_id, group in df.groupby(
        "company_id"
    ):

        # Preserve chronological source order as much
        # as possible using extracted numeric year.

        group = group.copy()

        group["_year_number"] = (
            group["year"]
            .astype(str)
            .str.extract(
                r"(\d{4})"
            )[0]
        )

        group[
            "_year_number"
        ] = pd.to_numeric(
            group["_year_number"],
            errors="coerce"
        )

        group = group.sort_values(
            [
                "_year_number",
                "year"
            ],
            na_position="last"
        )

        indexes = group.index.tolist()

        for position, row_index in enumerate(
            indexes
        ):

            if position < 5:
                continue

            revenue_result = (
                CAGREngine.calculate_with_flag(
                    beginning_value=group.iloc[
                        position - 5
                    ]["sales"],
                    ending_value=group.iloc[
                        position
                    ]["sales"],
                    years=5,
                    available_years=5
                )
            )

            pat_result = (
                CAGREngine.calculate_with_flag(
                    beginning_value=group.iloc[
                        position - 5
                    ]["net_profit"],
                    ending_value=group.iloc[
                        position
                    ]["net_profit"],
                    years=5,
                    available_years=5
                )
            )

            eps_result = (
                CAGREngine.calculate_with_flag(
                    beginning_value=group.iloc[
                        position - 5
                    ]["eps"],
                    ending_value=group.iloc[
                        position
                    ]["eps"],
                    years=5,
                    available_years=5
                )
            )

            df.at[
                row_index,
                "revenue_cagr_5yr"
            ] = revenue_result["value"]

            df.at[
                row_index,
                "pat_cagr_5yr"
            ] = pat_result["value"]

            df.at[
                row_index,
                "eps_cagr_5yr"
            ] = eps_result["value"]

    return df


# =========================================================
# Calculate Financial KPIs
# =========================================================

def calculate_kpis(df):

    print("\nCalculating financial KPIs...")

    records = []

    for _, row in df.iterrows():

        # ---------------------------------------------
        # Profitability
        # ---------------------------------------------

        npm = (
            FinancialRatioCalculator
            .net_profit_margin(
                row.get(
                    "net_profit"
                ),
                row.get(
                    "sales"
                )
            )
        )

        opm = (
            FinancialRatioCalculator
            .operating_profit_margin(
                row.get(
                    "operating_profit"
                ),
                row.get(
                    "sales"
                )
            )
        )

        roe = (
            FinancialRatioCalculator
            .return_on_equity(
                row.get(
                    "net_profit"
                ),
                row.get(
                    "equity_capital"
                ),
                row.get(
                    "reserves"
                )
            )
        )

        # ---------------------------------------------
        # Leverage
        # ---------------------------------------------

        debt_to_equity = (
            FinancialRatioCalculator
            .debt_to_equity(
                row.get(
                    "borrowings"
                ),
                row.get(
                    "equity_capital"
                ),
                row.get(
                    "reserves"
                )
            )
        )

        interest_coverage = (
            FinancialRatioCalculator
            .interest_coverage(
                row.get(
                    "operating_profit"
                ),
                row.get(
                    "other_income"
                ),
                row.get(
                    "interest"
                )
            )
        )

        asset_turnover = (
            FinancialRatioCalculator
            .asset_turnover(
                row.get(
                    "sales"
                ),
                row.get(
                    "total_assets"
                )
            )
        )

        # ---------------------------------------------
        # Cash Flow
        # ---------------------------------------------

        free_cash_flow = (
            CashFlowKPI.free_cash_flow(
                row.get(
                    "operating_activity"
                ),
                row.get(
                    "investing_activity"
                )
            )
        )

        # Using absolute investing cash flow
        # as current CapEx proxy.

        investing_activity = row.get(
            "investing_activity"
        )

        if (
            investing_activity is None
            or pd.isna(
                investing_activity
            )
        ):
            capex = None

        else:
            capex = abs(
                investing_activity
            )

        # ---------------------------------------------
        # Book Value Per Share
        # ---------------------------------------------

        equity_capital = row.get(
            "equity_capital"
        )

        reserves = row.get(
            "reserves"
        )

        book_value_per_share = None

        if (
            equity_capital is not None
            and not pd.isna(
                equity_capital
            )
            and equity_capital != 0
            and reserves is not None
            and not pd.isna(
                reserves
            )
        ):

            # Approximation based on available
            # balance-sheet fields.

            book_value_per_share = round(
                (
                    equity_capital
                    + reserves
                )
                / equity_capital,
                4
            )

        # ---------------------------------------------
        # Composite Score
        # ---------------------------------------------

        # Day 12 placeholder score based on currently
        # available core metrics.
        #
        # Full P10/P90 sector-relative composite scoring
        # will be implemented in Sprint 3 Day 17.

        score_values = []

        if roe is not None:
            score_values.append(
                min(
                    max(
                        roe,
                        0
                    ),
                    100
                )
            )

        if npm is not None:
            score_values.append(
                min(
                    max(
                        npm,
                        0
                    ),
                    100
                )
            )

        revenue_cagr = row.get(
            "revenue_cagr_5yr"
        )

        pat_cagr = row.get(
            "pat_cagr_5yr"
        )

        if (
            revenue_cagr is not None
            and not pd.isna(
                revenue_cagr
            )
        ):
            score_values.append(
                min(
                    max(
                        revenue_cagr,
                        0
                    ),
                    100
                )
            )

        if (
            pat_cagr is not None
            and not pd.isna(
                pat_cagr
            )
        ):
            score_values.append(
                min(
                    max(
                        pat_cagr,
                        0
                    ),
                    100
                )
            )

        if score_values:

            composite_score = round(
                sum(
                    score_values
                )
                / len(
                    score_values
                ),
                2
            )

        else:
            composite_score = None

        # ---------------------------------------------
        # Final Record
        # ---------------------------------------------

        record = {

            "company_id":
                row.get(
                    "company_id"
                ),

            "year":
                row.get(
                    "year"
                ),

            "net_profit_margin_pct":
                npm,

            "operating_profit_margin_pct":
                opm,

            "return_on_equity_pct":
                roe,

            "debt_to_equity":
                debt_to_equity,

            "interest_coverage":
                interest_coverage,

            "asset_turnover":
                asset_turnover,

            "free_cash_flow_cr":
                free_cash_flow,

            "capex_cr":
                capex,

            "earnings_per_share":
                row.get(
                    "eps"
                ),

            "book_value_per_share":
                book_value_per_share,

            "dividend_payout_ratio_pct":
                row.get(
                    "dividend_payout"
                ),

            "total_debt_cr":
                row.get(
                    "borrowings"
                ),

            "cash_from_operations_cr":
                row.get(
                    "operating_activity"
                ),

            "revenue_cagr_5yr":
                row.get(
                    "revenue_cagr_5yr"
                ),

            "pat_cagr_5yr":
                row.get(
                    "pat_cagr_5yr"
                ),

            "eps_cagr_5yr":
                row.get(
                    "eps_cagr_5yr"
                ),

            "composite_quality_score":
                composite_score
        }

        records.append(
            record
        )

    return pd.DataFrame(
        records
    )


# =========================================================
# Save to SQLite
# =========================================================

def save_to_database(
    conn,
    output_df
):

    print(
        "\nWriting financial ratios..."
    )

    columns = [
        "company_id",
        "year",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "capex_cr",
        "earnings_per_share",
        "book_value_per_share",
        "dividend_payout_ratio_pct",
        "total_debt_cr",
        "cash_from_operations_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "composite_quality_score"
    ]

    placeholders = ", ".join(
        ["?"] * len(columns)
    )

    column_sql = ", ".join(
        columns
    )

    update_sql = ", ".join(
        [
            f"{column}=excluded.{column}"
            for column in columns
            if column not in (
                "company_id",
                "year"
            )
        ]
    )

    sql = f"""
        INSERT INTO financial_ratios
        (
            {column_sql}
        )
        VALUES
        (
            {placeholders}
        )

        ON CONFLICT(company_id, year)

        DO UPDATE SET
            {update_sql}
    """

    rows = []

    for _, row in output_df.iterrows():

        rows.append(
            tuple(
                safe_value(
                    row[column]
                )
                for column in columns
            )
        )

    conn.executemany(
        sql,
        rows
    )

    conn.commit()

    print(
        f"Processed rows: {len(rows)}"
    )


# =========================================================
# Main
# =========================================================

def main():

    print(
        "\n"
        "=============================================="
    )

    print(
        "Sprint 2 - Day 12"
    )

    print(
        "Financial Ratio Table Population"
    )

    print(
        "=============================================="
    )

    conn = sqlite3.connect(
        DB_PATH
    )

    try:

        conn.execute(
            "PRAGMA foreign_keys = ON"
        )

        ensure_columns(
            conn
        )

        profit, balance, cashflow = (
            load_data(
                conn
            )
        )

        merged = merge_data(
            profit,
            balance,
            cashflow
        )

        merged = add_cagr_columns(
            merged
        )

        output_df = calculate_kpis(
            merged
        )

        save_to_database(
            conn,
            output_df
        )

        row_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM financial_ratios
            """
        ).fetchone()[0]

        print(
            "\n"
            "=============================================="
        )

        print(
            f"financial_ratios rows: {row_count}"
        )

        if row_count >= 1100:

            print(
                "PASS: Sprint 2 row target achieved."
            )

        else:

            print(
                "WARNING: Row count is below 1,100."
            )

        print(
            "=============================================="
        )

    finally:

        conn.close()


if __name__ == "__main__":
    main()