"""
src/analytics/ratio_edge_cases.py

N100 Financial Intelligence Platform
Sprint 2 - Day 13
Bank ROCE Carve-Out & Edge Case Analysis
"""

import sqlite3
from pathlib import Path
from datetime import datetime

import pandas as pd

from src.analytics.ratios import FinancialRatioCalculator


# =========================================================
# Paths
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = OUTPUT_DIR / "ratio_edge_cases.log"


# =========================================================
# Helpers
# =========================================================

def is_missing(value):
    return value is None or pd.isna(value)


def classify_anomaly(source_value, calculated_value, difference):

    if is_missing(source_value) or is_missing(calculated_value):
        return "data source issue"

    if difference >= 50:
        return "data source issue"

    if difference >= 10:
        return "version difference"

    return "formula discrepancy"


# =========================================================
# Load Data
# =========================================================

def load_data(conn):

    # broad_sector is stored in sectors table,
    # not directly in companies table.

    companies = pd.read_sql_query(
        """
        SELECT
            c.id AS company_id,
            c.company_name,
            s.broad_sector,
            c.roe_percentage,
            c.roce_percentage
        FROM companies c
        LEFT JOIN sectors s
            ON c.id = s.company_id
        """,
        conn,
    )

    profit = pd.read_sql_query(
        """
        SELECT *
        FROM profitandloss
        """,
        conn,
    )

    balance = pd.read_sql_query(
        """
        SELECT *
        FROM balancesheet
        """,
        conn,
    )

    return companies, profit, balance


# =========================================================
# Merge Data
# =========================================================

def prepare_data(companies, profit, balance):

    # Only use company-year records that have both
    # P&L and Balance Sheet information.

    merged = profit.merge(
        balance,
        on=["company_id", "year"],
        how="inner",
        suffixes=("", "_bs"),
    )

    merged = merged.merge(
        companies,
        on="company_id",
        how="left",
    )

    return merged


# =========================================================
# Calculate ROE and ROCE
# =========================================================

def calculate_ratios(df):

    results = []

    for _, row in df.iterrows():

        roe = FinancialRatioCalculator.return_on_equity(
            net_profit=row.get("net_profit"),
            equity_capital=row.get("equity_capital"),
            reserves=row.get("reserves"),
        )

        roce = (
            FinancialRatioCalculator
            .return_on_capital_employed(
                operating_profit=row.get("operating_profit"),
                other_income=row.get("other_income"),
                equity_capital=row.get("equity_capital"),
                reserves=row.get("reserves"),
                borrowings=row.get("borrowings"),
            )
        )

        results.append(
            {
                "company_id": row.get("company_id"),
                "company_name": row.get("company_name"),
                "year": row.get("year"),
                "broad_sector": row.get("broad_sector"),
                "source_roe": row.get("roe_percentage"),
                "calculated_roe": roe,
                "source_roce": row.get("roce_percentage"),
                "calculated_roce": roce,
            }
        )

    return pd.DataFrame(results)


# =========================================================
# Select Latest Comparable Record Per Company
# =========================================================

def latest_company_records(df):

    df = df.copy()

    # Handles formats such as:
    # Mar 2024
    # Sep 2024
    # Mar-24

    year_4 = (
        df["year"]
        .astype(str)
        .str.extract(r"(\d{4})")[0]
    )

    year_2 = (
        df["year"]
        .astype(str)
        .str.extract(r"(\d{2})$")[0]
    )

    df["_year_number"] = pd.to_numeric(
        year_4,
        errors="coerce",
    )

    short_year = pd.to_numeric(
        year_2,
        errors="coerce",
    )

    missing = df["_year_number"].isna()

    df.loc[
        missing,
        "_year_number"
    ] = 2000 + short_year[missing]

    df = df.sort_values(
        [
            "company_id",
            "_year_number",
            "year",
        ],
        na_position="first",
    )

    latest = (
        df.groupby(
            "company_id",
            as_index=False,
        )
        .tail(1)
        .copy()
    )

    return latest


# =========================================================
# Financial Sector Carve-Out
# =========================================================

def financial_sector_summary(df):

    financials = df[
        df["broad_sector"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("financials")
    ].copy()

    return financials


# =========================================================
# Detect ROE / ROCE Anomalies
# =========================================================

def detect_anomalies(df):

    anomalies = []

    for _, row in df.iterrows():

        # -------------------------------------------------
        # ROCE
        # -------------------------------------------------

        source_roce = row.get("source_roce")
        calculated_roce = row.get("calculated_roce")

        if (
            not is_missing(source_roce)
            and not is_missing(calculated_roce)
        ):

            difference = abs(
                float(source_roce)
                - float(calculated_roce)
            )

            if difference > 5:

                anomalies.append(
                    {
                        "company_id":
                            row.get("company_id"),

                        "company_name":
                            row.get("company_name"),

                        "year":
                            row.get("year"),

                        "sector":
                            row.get("broad_sector"),

                        "metric":
                            "ROCE",

                        "source_value":
                            source_roce,

                        "calculated_value":
                            calculated_roce,

                        "difference":
                            difference,

                        "category":
                            classify_anomaly(
                                source_roce,
                                calculated_roce,
                                difference,
                            ),

                        "explanation":
                            (
                                "Computed ROCE differs from "
                                "the source ROCE by more than "
                                "5 percentage points."
                            ),
                    }
                )

        # -------------------------------------------------
        # ROE
        # -------------------------------------------------

        source_roe = row.get("source_roe")
        calculated_roe = row.get("calculated_roe")

        if (
            not is_missing(source_roe)
            and not is_missing(calculated_roe)
        ):

            difference = abs(
                float(source_roe)
                - float(calculated_roe)
            )

            if difference > 5:

                anomalies.append(
                    {
                        "company_id":
                            row.get("company_id"),

                        "company_name":
                            row.get("company_name"),

                        "year":
                            row.get("year"),

                        "sector":
                            row.get("broad_sector"),

                        "metric":
                            "ROE",

                        "source_value":
                            source_roe,

                        "calculated_value":
                            calculated_roe,

                        "difference":
                            difference,

                        "category":
                            classify_anomaly(
                                source_roe,
                                calculated_roe,
                                difference,
                            ),

                        "explanation":
                            (
                                "Source ROE is retained for "
                                "display only. Computed ROE "
                                "should be used for analytics."
                            ),
                    }
                )

    return anomalies


# =========================================================
# Write Edge Case Log
# =========================================================

def write_log(anomalies, financials):

    with open(
        LOG_FILE,
        "w",
        encoding="utf-8",
    ) as log:

        log.write(
            "N100 FINANCIAL INTELLIGENCE PLATFORM\n"
        )

        log.write(
            "SPRINT 2 - DAY 13\n"
        )

        log.write(
            "RATIO EDGE CASE REPORT\n"
        )

        log.write(
            "=" * 70 + "\n"
        )

        log.write(
            f"Generated: {datetime.now()}\n\n"
        )

        # -------------------------------------------------
        # Financial Sector Carve-Out
        # -------------------------------------------------

        log.write(
            "FINANCIAL SECTOR CARVE-OUT\n"
        )

        log.write(
            "-" * 70 + "\n"
        )

        log.write(
            "Companies in the Financials broad sector are "
            "exempt from the standard high Debt-to-Equity "
            "warning because high leverage is structurally "
            "normal for banks, NBFCs and similar financial "
            "institutions.\n\n"
        )

        log.write(
            f"Financial-sector companies found: "
            f"{len(financials)}\n\n"
        )

        for _, row in financials.iterrows():

            log.write(
                f"{row['company_id']} | "
                f"{row['company_name']} | "
                f"Year: {row['year']} | "
                f"Calculated ROCE: "
                f"{row['calculated_roce']}\n"
            )

        # -------------------------------------------------
        # Anomalies
        # -------------------------------------------------

        log.write(
            "\n" + "=" * 70 + "\n"
        )

        log.write(
            "ROE / ROCE ANOMALIES\n"
        )

        log.write(
            "-" * 70 + "\n"
        )

        log.write(
            f"Total anomalies: {len(anomalies)}\n\n"
        )

        if not anomalies:

            log.write(
                "No anomalies above the "
                "5 percentage-point threshold.\n"
            )

        for number, item in enumerate(
            anomalies,
            start=1,
        ):

            log.write(
                f"[{number}]\n"
            )

            log.write(
                f"Company ID: "
                f"{item['company_id']}\n"
            )

            log.write(
                f"Company: "
                f"{item['company_name']}\n"
            )

            log.write(
                f"Year: "
                f"{item['year']}\n"
            )

            log.write(
                f"Sector: "
                f"{item['sector']}\n"
            )

            log.write(
                f"Metric: "
                f"{item['metric']}\n"
            )

            log.write(
                f"Source Value: "
                f"{item['source_value']}\n"
            )

            log.write(
                f"Calculated Value: "
                f"{item['calculated_value']}\n"
            )

            log.write(
                f"Difference: "
                f"{item['difference']:.2f}\n"
            )

            log.write(
                f"Category: "
                f"{item['category']}\n"
            )

            log.write(
                f"Explanation: "
                f"{item['explanation']}\n\n"
            )

        # -------------------------------------------------
        # Category Summary
        # -------------------------------------------------

        log.write(
            "=" * 70 + "\n"
        )

        log.write(
            "ANOMALY CATEGORY SUMMARY\n"
        )

        log.write(
            "-" * 70 + "\n"
        )

        categories = {}

        for item in anomalies:

            category = item["category"]

            categories[category] = (
                categories.get(
                    category,
                    0,
                )
                + 1
            )

        if categories:

            for category, count in categories.items():

                log.write(
                    f"{category}: {count}\n"
                )

        else:

            log.write(
                "No anomaly categories recorded.\n"
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
        "Sprint 2 - Day 13"
    )

    print(
        "Bank ROCE Carve-Out & Edge Case Analysis"
    )

    print(
        "=============================================="
    )

    conn = sqlite3.connect(
        DB_PATH
    )

    try:

        companies, profit, balance = load_data(
            conn
        )

        print(
            f"\nCompanies loaded: "
            f"{len(companies)}"
        )

        print(
            f"P&L rows: "
            f"{len(profit)}"
        )

        print(
            f"Balance Sheet rows: "
            f"{len(balance)}"
        )

        merged = prepare_data(
            companies,
            profit,
            balance,
        )

        print(
            f"Comparable company-year rows: "
            f"{len(merged)}"
        )

        ratios = calculate_ratios(
            merged
        )

        latest = latest_company_records(
            ratios
        )

        print(
            f"Companies analysed: "
            f"{len(latest)}"
        )

        financials = financial_sector_summary(
            latest
        )

        print(
            f"Financial-sector companies: "
            f"{len(financials)}"
        )

        anomalies = detect_anomalies(
            latest
        )

        print(
            f"ROE/ROCE anomalies: "
            f"{len(anomalies)}"
        )

        write_log(
            anomalies,
            financials,
        )

        print(
            "\nEdge case log generated:"
        )

        print(
            LOG_FILE
        )

        print(
            "\nDay 13 analysis completed successfully."
        )

    finally:

        conn.close()


if __name__ == "__main__":
    main()