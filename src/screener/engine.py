"""
src/screener/engine.py

N100 Financial Intelligence Platform
Sprint 3 - Day 15
Financial Screener Filter Engine
"""

from pathlib import Path
import sqlite3

import pandas as pd
import yaml


BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "db" / "nifty100.db"
CONFIG_PATH = BASE_DIR / "config" / "screener_config.yaml"


class ScreenerEngine:
    """Filter N100 companies using configurable financial metrics."""

    FINANCIAL_SECTORS = {
        "financials",
        "financial services",
        "banking",
        "banks",
        "insurance",
    }

    def __init__(self, db_path=DB_PATH, config_path=CONFIG_PATH):
        self.db_path = Path(db_path)
        self.config_path = Path(config_path)
        self.config = self.load_config()

    def load_config(self):
        """Load screener configuration from YAML."""

        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Screener config not found: {self.config_path}"
            )

        with open(self.config_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}

    def load_data(self):
        """Load company, sector, financial ratio and P&L data."""

        with sqlite3.connect(self.db_path) as conn:

            query = """
            SELECT
                f.company_id,
                c.company_name,
                f.year,
                s.broad_sector,

                f.return_on_equity_pct,
                f.debt_to_equity,
                f.interest_coverage,
                f.asset_turnover,
                f.free_cash_flow_cr,
                f.operating_profit_margin_pct,
                f.revenue_cagr_5yr,
                f.pat_cagr_5yr,
                f.eps_cagr_5yr,
                f.composite_quality_score,

                p.sales,
                p.net_profit

            FROM financial_ratios f

            JOIN companies c
                ON f.company_id = c.id

            LEFT JOIN sectors s
                ON f.company_id = s.company_id

            LEFT JOIN profitandloss p
                ON f.company_id = p.company_id
                AND f.year = p.year
            """

            return pd.read_sql_query(query, conn)

    @staticmethod
    def _apply_min_filter(df, column, value):
        """Keep rows where column >= minimum value."""

        if value is None or column not in df.columns:
            return df

        return df[
            df[column].notna()
            & (df[column] >= value)
        ]

    @staticmethod
    def _apply_max_filter(df, column, value):
        """Keep rows where column <= maximum value."""

        if value is None or column not in df.columns:
            return df

        return df[
            df[column].notna()
            & (df[column] <= value)
        ]

    def apply_debt_to_equity_filter(self, df, max_value):
        """
        Apply Debt-to-Equity filter.

        Financial-sector companies may be exempt because leverage
        is structurally different for banks and financial institutions.
        """

        if max_value is None:
            return df

        settings = self.config.get("settings", {})

        exemption_enabled = settings.get(
            "financial_sector_de_exemption",
            True,
        )

        if not exemption_enabled:
            return self._apply_max_filter(
                df,
                "debt_to_equity",
                max_value,
            )

        sector = (
            df["broad_sector"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
        )

        is_financial = sector.isin(self.FINANCIAL_SECTORS)

        valid_non_financial = (
            df["debt_to_equity"].notna()
            & (df["debt_to_equity"] <= max_value)
        )

        return df[
            is_financial | valid_non_financial
        ]

    def apply_icr_filter(self, df, min_value):
        """
        Apply Interest Coverage Ratio filter.

        If configured, debt-free companies with zero/NULL debt
        can be treated as having infinite interest coverage.
        """

        if min_value is None:
            return df

        settings = self.config.get("settings", {})

        debt_free_as_infinity = settings.get(
            "debt_free_icr_as_infinity",
            True,
        )

        valid_icr = (
            df["interest_coverage"].notna()
            & (df["interest_coverage"] >= min_value)
        )

        if not debt_free_as_infinity:
            return df[valid_icr]

        debt_free = (
            df["debt_to_equity"].notna()
            & (df["debt_to_equity"] == 0)
        )

        return df[
            valid_icr | debt_free
        ]

    def apply_filters(self, df, filters=None):
        """Apply all configured screener filters."""

        if filters is None:
            filters = self.config.get("filters", {})

        result = df.copy()

        # Profitability
        result = self._apply_min_filter(
            result,
            "return_on_equity_pct",
            filters.get("roe_min"),
        )

        result = self._apply_min_filter(
            result,
            "operating_profit_margin_pct",
            filters.get("opm_min"),
        )

        result = self._apply_min_filter(
            result,
            "net_profit",
            filters.get("net_profit_min"),
        )

        # Growth
        result = self._apply_min_filter(
            result,
            "revenue_cagr_5yr",
            filters.get("revenue_cagr_5yr_min"),
        )

        result = self._apply_min_filter(
            result,
            "pat_cagr_5yr",
            filters.get("pat_cagr_5yr_min"),
        )

        result = self._apply_min_filter(
            result,
            "eps_cagr_5yr",
            filters.get("eps_cagr_5yr_min"),
        )

        # Cash flow
        result = self._apply_min_filter(
            result,
            "free_cash_flow_cr",
            filters.get("fcf_min"),
        )

        # Efficiency
        result = self._apply_min_filter(
            result,
            "asset_turnover",
            filters.get("asset_turnover_min"),
        )

        result = self._apply_min_filter(
            result,
            "sales",
            filters.get("sales_min"),
        )

        # Leverage
        result = self.apply_debt_to_equity_filter(
            result,
            filters.get("debt_to_equity_max"),
        )

        result = self.apply_icr_filter(
            result,
            filters.get("icr_min"),
        )

        # The following filters are reserved for valuation/market data.
        # They will activate when corresponding columns are available:
        #
        # pe_max
        # pb_max
        # dividend_yield_min
        # market_cap_min

        return result

    def sort_results(self, df):
        """Sort results using configured quality metric."""

        settings = self.config.get("settings", {})

        sort_by = settings.get(
            "sort_by",
            "composite_quality_score",
        )

        ascending = settings.get(
            "sort_ascending",
            False,
        )

        if sort_by not in df.columns:
            return df

        return df.sort_values(
            by=sort_by,
            ascending=ascending,
            na_position="last",
        )

    def screen(self, filters=None, year=None):
        """Run the complete screener."""

        df = self.load_data()

        if year is not None:
            df = df[
                df["year"] == year
            ]

        result = self.apply_filters(
            df,
            filters,
        )

        result = self.sort_results(
            result,
        )

        return result.reset_index(drop=True)


def main():
    print("=" * 50)
    print("Sprint 3 - Day 15")
    print("N100 Financial Screener Engine")
    print("=" * 50)

    engine = ScreenerEngine()

    # Day 15 validation filter
    filters = {
        "roe_min": 15,
        "debt_to_equity_max": 1,
    }

    results = engine.screen(
        filters=filters,
        year="Mar 2024",
    )

    print(f"\nCompanies matched: {len(results)}")

    display_columns = [
        "company_id",
        "company_name",
        "broad_sector",
        "year",
        "return_on_equity_pct",
        "debt_to_equity",
        "composite_quality_score",
    ]

    print(
        results[
            [
                column
                for column in display_columns
                if column in results.columns
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

    print("\nDay 15 screener engine completed successfully.")


if __name__ == "__main__":
    main()