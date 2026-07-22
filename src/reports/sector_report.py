"""
src/reports/sector_report.py

N100 Financial Intelligence Platform
Sprint 4 - Day 20
Sector Intelligence Engine
"""

import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class SectorReportGenerator:

    def __init__(self, db_path=DB_PATH):
        self.db_path = Path(db_path)

    def _connect(self):
        return sqlite3.connect(self.db_path)

    # =====================================================
    # Load Company-Level Sector Data
    # =====================================================

    def load_company_data(
        self,
        financial_year="Mar 2024",
        market_year="2024",
    ):

        query = """
        SELECT
            c.id AS company_id,
            c.company_name,

            s.broad_sector,
            s.sub_sector,
            s.index_weight_pct,
            s.market_cap_category,

            m.market_cap_crore,
            m.pe_ratio,
            m.pb_ratio,
            m.dividend_yield_pct,

            f.net_profit_margin_pct,
            f.operating_profit_margin_pct,
            f.return_on_equity_pct,
            f.debt_to_equity,
            f.interest_coverage,
            f.asset_turnover,
            f.free_cash_flow_cr,
            f.revenue_cagr_5yr,
            f.pat_cagr_5yr,
            f.eps_cagr_5yr,
            f.composite_quality_score

        FROM companies c

        INNER JOIN sectors s
            ON c.id = s.company_id

        LEFT JOIN market_cap m
            ON c.id = m.company_id
            AND m.year = ?

        LEFT JOIN financial_ratios f
            ON c.id = f.company_id
            AND f.year = ?

        ORDER BY
            s.broad_sector,
            c.company_name
        """

        with self._connect() as conn:

            df = pd.read_sql_query(
                query,
                conn,
                params=[
                    market_year,
                    financial_year,
                ],
            )

        return df

    # =====================================================
    # Sector Summary
    # =====================================================

    def generate(
        self,
        financial_year="Mar 2024",
        market_year="2024",
    ):

        df = self.load_company_data(
            financial_year=financial_year,
            market_year=market_year,
        )

        summary = (
            df.groupby(
                "broad_sector",
                dropna=False,
            )
            .agg(
                company_count=(
                    "company_id",
                    "nunique",
                ),

                total_market_cap_crore=(
                    "market_cap_crore",
                    "sum",
                ),

                average_market_cap_crore=(
                    "market_cap_crore",
                    "mean",
                ),

                average_pe_ratio=(
                    "pe_ratio",
                    "mean",
                ),

                average_pb_ratio=(
                    "pb_ratio",
                    "mean",
                ),

                average_dividend_yield_pct=(
                    "dividend_yield_pct",
                    "mean",
                ),

                average_roe_pct=(
                    "return_on_equity_pct",
                    "mean",
                ),

                median_roe_pct=(
                    "return_on_equity_pct",
                    "median",
                ),

                average_opm_pct=(
                    "operating_profit_margin_pct",
                    "mean",
                ),

                average_debt_to_equity=(
                    "debt_to_equity",
                    "mean",
                ),

                average_asset_turnover=(
                    "asset_turnover",
                    "mean",
                ),

                average_revenue_cagr_5yr=(
                    "revenue_cagr_5yr",
                    "mean",
                ),

                average_pat_cagr_5yr=(
                    "pat_cagr_5yr",
                    "mean",
                ),

                average_eps_cagr_5yr=(
                    "eps_cagr_5yr",
                    "mean",
                ),

                total_free_cash_flow_cr=(
                    "free_cash_flow_cr",
                    "sum",
                ),

                average_quality_score=(
                    "composite_quality_score",
                    "mean",
                ),
            )
            .reset_index()
        )

        summary = summary.sort_values(
            "average_quality_score",
            ascending=False,
            na_position="last",
        )

        summary.reset_index(
            drop=True,
            inplace=True,
        )

        summary.insert(
            0,
            "sector_rank",
            range(
                1,
                len(summary) + 1,
            ),
        )

        return summary

    # =====================================================
    # Single Sector
    # =====================================================

    def get_sector(
        self,
        sector_name,
        financial_year="Mar 2024",
        market_year="2024",
    ):

        df = self.load_company_data(
            financial_year=financial_year,
            market_year=market_year,
        )

        result = df[
            df["broad_sector"]
            .fillna("")
            .str.strip()
            .str.casefold()
            == sector_name.strip().casefold()
        ].copy()

        if result.empty:
            raise ValueError(
                f"Sector '{sector_name}' not found."
            )

        result = result.sort_values(
            "composite_quality_score",
            ascending=False,
            na_position="last",
        )

        result.reset_index(
            drop=True,
            inplace=True,
        )

        return result

    # =====================================================
    # Sector Leaders
    # =====================================================

    def sector_leaders(
        self,
        sector_name,
        limit=5,
        financial_year="Mar 2024",
        market_year="2024",
    ):

        sector_df = self.get_sector(
            sector_name,
            financial_year=financial_year,
            market_year=market_year,
        )

        return (
            sector_df
            .head(limit)
            .reset_index(drop=True)
        )

    # =====================================================
    # Export
    # =====================================================

    def export_csv(
        self,
        output_path=None,
        financial_year="Mar 2024",
        market_year="2024",
    ):

        report = self.generate(
            financial_year=financial_year,
            market_year=market_year,
        )

        if output_path is None:
            output_path = (
                OUTPUT_DIR /
                "sector_intelligence_report.csv"
            )
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        report.to_csv(
            output_path,
            index=False,
        )

        return output_path


# =========================================================
# Main
# =========================================================

def main():

    print("=" * 72)
    print("Sprint 4 - Day 20")
    print("N100 Sector Intelligence Engine")
    print("=" * 72)

    generator = SectorReportGenerator()

    report = generator.generate()

    print(
        f"\nSectors analysed: {len(report)}"
    )

    print(
        "Companies analysed:",
        int(report["company_count"].sum()),
    )

    print("\nSector Intelligence Ranking")
    print("-" * 72)

    display_columns = [
        "sector_rank",
        "broad_sector",
        "company_count",
        "total_market_cap_crore",
        "average_roe_pct",
        "average_debt_to_equity",
        "average_revenue_cagr_5yr",
        "average_pat_cagr_5yr",
        "average_quality_score",
    ]

    print(
        report[display_columns]
        .to_string(index=False)
    )

    print("\nTop Financial Sector Companies")
    print("-" * 72)

    leaders = generator.sector_leaders(
        "Financials",
        limit=5,
    )

    leader_columns = [
        "company_id",
        "company_name",
        "return_on_equity_pct",
        "debt_to_equity",
        "revenue_cagr_5yr",
        "composite_quality_score",
    ]

    print(
        leaders[leader_columns]
        .to_string(index=False)
    )

    output = generator.export_csv()

    print(
        f"\nSector report saved to: {output}"
    )

    print(
        "\nDay 20 Sector Intelligence "
        "completed successfully."
    )


if __name__ == "__main__":
    main()