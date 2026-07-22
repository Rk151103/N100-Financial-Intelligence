"""
src/reports/company_report.py

N100 Financial Intelligence Platform
Sprint 4 - Day 18
Company Intelligence Report Generator
"""

import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class CompanyReportGenerator:

    def __init__(self, db_path=DB_PATH):
        self.db_path = Path(db_path)

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def generate(
        self,
        company_id=None,
        financial_year="Mar 2024",
        market_year="2024",
    ):
        """
        Generate company intelligence data.

        If company_id is None, reports for all companies
        are returned.
        """

        query = """
        SELECT
            c.id AS company_id,
            c.company_name,
            c.book_value,
            c.roe_percentage AS source_roe_pct,
            c.roce_percentage AS source_roce_pct,

            s.broad_sector,
            s.sub_sector,
            s.index_weight_pct,
            s.market_cap_category,

            m.market_cap_crore,
            m.enterprise_value_crore,
            m.pe_ratio,
            m.pb_ratio,
            m.ev_ebitda,
            m.dividend_yield_pct,

            f.net_profit_margin_pct,
            f.operating_profit_margin_pct,
            f.return_on_equity_pct,
            f.debt_to_equity,
            f.interest_coverage,
            f.asset_turnover,
            f.free_cash_flow_cr,
            f.capex_cr,
            f.earnings_per_share,
            f.book_value_per_share,
            f.dividend_payout_ratio_pct,
            f.total_debt_cr,
            f.cash_from_operations_cr,
            f.revenue_cagr_5yr,
            f.pat_cagr_5yr,
            f.eps_cagr_5yr,
            f.composite_quality_score

        FROM companies c

        LEFT JOIN sectors s
            ON c.id = s.company_id

        LEFT JOIN market_cap m
            ON c.id = m.company_id
            AND m.year = ?

        LEFT JOIN financial_ratios f
            ON c.id = f.company_id
            AND f.year = ?

        WHERE (? IS NULL OR c.id = ?)

        ORDER BY
            f.composite_quality_score DESC,
            c.company_name ASC
        """

        with self._connect() as conn:
            df = pd.read_sql_query(
                query,
                conn,
                params=[
                    market_year,
                    financial_year,
                    company_id,
                    company_id,
                ],
            )

        return df

    def generate_by_name(
        self,
        company_name,
        financial_year="Mar 2024",
        market_year="2024",
    ):
        """
        Generate report for one company using its name.
        """

        df = self.generate(
            financial_year=financial_year,
            market_year=market_year,
        )

        result = df[
            df["company_name"]
            .fillna("")
            .str.strip()
            .str.casefold()
            == company_name.strip().casefold()
        ].copy()

        if result.empty:
            raise ValueError(
                f"Company '{company_name}' not found."
            )

        return result.reset_index(drop=True)

    def export_csv(
        self,
        output_path=None,
        company_id=None,
        financial_year="Mar 2024",
        market_year="2024",
    ):
        """
        Export company intelligence report to CSV.
        """

        df = self.generate(
            company_id=company_id,
            financial_year=financial_year,
            market_year=market_year,
        )

        if output_path is None:
            output_path = OUTPUT_DIR / "company_intelligence_report.csv"
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        df.to_csv(
            output_path,
            index=False,
        )

        return output_path

    @staticmethod
    def quality_label(score):
        """
        Convert composite quality score into a simple label.
        """

        if pd.isna(score):
            return "Unknown"

        if score >= 40:
            return "High Quality"

        if score >= 20:
            return "Moderate Quality"

        return "Watchlist"

    def add_quality_labels(self, df):
        """
        Add quality labels to report dataframe.
        """

        result = df.copy()

        result["quality_label"] = (
            result["composite_quality_score"]
            .apply(self.quality_label)
        )

        return result


def main():

    print("=" * 70)
    print("Sprint 4 - Day 18")
    print("N100 Company Intelligence Report Generator")
    print("=" * 70)

    generator = CompanyReportGenerator()

    df = generator.generate(
        financial_year="Mar 2024",
        market_year="2024",
    )

    df = generator.add_quality_labels(df)

    print(f"\nCompanies loaded: {len(df)}")

    display_columns = [
        "company_id",
        "company_name",
        "broad_sector",
        "market_cap_crore",
        "pe_ratio",
        "return_on_equity_pct",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "composite_quality_score",
        "quality_label",
    ]

    available_columns = [
        column
        for column in display_columns
        if column in df.columns
    ]

    print("\nTop 10 Companies")
    print("-" * 70)

    print(
        df[available_columns]
        .head(10)
        .to_string(index=False)
    )

    output_file = (
        OUTPUT_DIR /
        "company_intelligence_report.csv"
    )

    df.to_csv(
        output_file,
        index=False,
    )

    print(
        f"\nReport saved to: {output_file}"
    )

    print(
        "\nDay 18 Company Intelligence Report "
        "completed successfully."
    )


if __name__ == "__main__":
    main()