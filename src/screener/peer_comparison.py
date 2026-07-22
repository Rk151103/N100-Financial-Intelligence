"""
src/screener/peer_comparison.py

N100 Financial Intelligence Platform
Sprint 3 - Day 17
Peer Comparison Engine
"""

from pathlib import Path
import sqlite3

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "db" / "nifty100.db"


class PeerComparisonEngine:
    """Compare a company against companies in the same broad sector."""

    DEFAULT_METRICS = [
        "return_on_equity_pct",
        "debt_to_equity",
        "operating_profit_margin_pct",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "asset_turnover",
        "composite_quality_score",
    ]

    # Higher values are considered better for these metrics.
    HIGHER_IS_BETTER = {
        "return_on_equity_pct",
        "operating_profit_margin_pct",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "asset_turnover",
        "composite_quality_score",
    }

    # Lower values are considered better.
    LOWER_IS_BETTER = {
        "debt_to_equity",
    }

    def __init__(self, db_path=DB_PATH):
        self.db_path = Path(db_path)

    def load_data(self, year="Mar 2024"):
        """Load company, sector and financial-ratio data."""

        query = """
        SELECT
            f.company_id,
            c.company_name,
            s.broad_sector,
            f.year,
            f.return_on_equity_pct,
            f.debt_to_equity,
            f.interest_coverage,
            f.asset_turnover,
            f.free_cash_flow_cr,
            f.operating_profit_margin_pct,
            f.revenue_cagr_5yr,
            f.pat_cagr_5yr,
            f.eps_cagr_5yr,
            f.composite_quality_score
        FROM financial_ratios f
        JOIN companies c
            ON f.company_id = c.id
        LEFT JOIN sectors s
            ON f.company_id = s.company_id
        WHERE f.year = ?
        """

        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(
                query,
                conn,
                params=(year,),
            )

    @staticmethod
    def _clean_company_id(company_id):
        if company_id is None:
            return None

        return str(company_id).strip().upper()

    def get_company(self, company_id, year="Mar 2024"):
        """Return one company's row."""

        company_id = self._clean_company_id(company_id)
        df = self.load_data(year)

        company = df[
            df["company_id"]
            .astype(str)
            .str.upper()
            == company_id
        ]

        if company.empty:
            raise ValueError(
                f"Company '{company_id}' not found for {year}."
            )

        return company.iloc[0]

    def get_peers(
        self,
        company_id,
        year="Mar 2024",
        include_company=True,
    ):
        """Return companies belonging to the same broad sector."""

        company = self.get_company(
            company_id,
            year,
        )

        sector = company["broad_sector"]

        if pd.isna(sector) or not str(sector).strip():
            raise ValueError(
                f"No broad sector available for {company_id}."
            )

        df = self.load_data(year)

        peers = df[
            df["broad_sector"] == sector
        ].copy()

        if not include_company:
            peers = peers[
                peers["company_id"] != company["company_id"]
            ]

        return peers.reset_index(drop=True)

    def sector_statistics(
        self,
        company_id,
        year="Mar 2024",
        metrics=None,
    ):
        """Calculate sector mean, median, min and max."""

        metrics = metrics or self.DEFAULT_METRICS

        peers = self.get_peers(
            company_id,
            year,
            include_company=True,
        )

        available_metrics = [
            metric
            for metric in metrics
            if metric in peers.columns
        ]

        records = []

        for metric in available_metrics:
            values = pd.to_numeric(
                peers[metric],
                errors="coerce",
            ).dropna()

            if values.empty:
                continue

            records.append(
                {
                    "metric": metric,
                    "count": int(values.count()),
                    "mean": round(float(values.mean()), 2),
                    "median": round(float(values.median()), 2),
                    "minimum": round(float(values.min()), 2),
                    "maximum": round(float(values.max()), 2),
                }
            )

        return pd.DataFrame(records)

    def metric_rank(
        self,
        company_id,
        metric,
        year="Mar 2024",
    ):
        """Return company rank within its sector for one metric."""

        peers = self.get_peers(
            company_id,
            year,
            include_company=True,
        )

        if metric not in peers.columns:
            raise ValueError(
                f"Metric '{metric}' is not available."
            )

        data = peers[
            ["company_id", "company_name", metric]
        ].copy()

        data[metric] = pd.to_numeric(
            data[metric],
            errors="coerce",
        )

        data = data.dropna(
            subset=[metric]
        )

        company_id = self._clean_company_id(
            company_id
        )

        if company_id not in data["company_id"].values:
            return None

        if metric in self.LOWER_IS_BETTER:
            ascending = True
        else:
            ascending = False

        data = data.sort_values(
            metric,
            ascending=ascending,
        ).reset_index(drop=True)

        data["rank"] = (
            data[metric]
            .rank(
                method="min",
                ascending=ascending,
            )
            .astype(int)
        )

        company_row = data[
            data["company_id"] == company_id
        ].iloc[0]

        return {
            "company_id": company_id,
            "metric": metric,
            "value": float(company_row[metric]),
            "rank": int(company_row["rank"]),
            "peer_count": len(data),
        }

    def comparison_summary(
        self,
        company_id,
        year="Mar 2024",
        metrics=None,
    ):
        """Compare a company with sector median and calculate ranks."""

        metrics = metrics or self.DEFAULT_METRICS

        company = self.get_company(
            company_id,
            year,
        )

        peers = self.get_peers(
            company_id,
            year,
            include_company=True,
        )

        records = []

        for metric in metrics:

            if metric not in peers.columns:
                continue

            values = pd.to_numeric(
                peers[metric],
                errors="coerce",
            ).dropna()

            company_value = pd.to_numeric(
                pd.Series([company[metric]]),
                errors="coerce",
            ).iloc[0]

            if values.empty or pd.isna(company_value):
                continue

            median = float(values.median())

            rank_info = self.metric_rank(
                company_id,
                metric,
                year,
            )

            if rank_info is None:
                continue

            if metric in self.LOWER_IS_BETTER:
                better_than_median = (
                    company_value <= median
                )
            else:
                better_than_median = (
                    company_value >= median
                )

            records.append(
                {
                    "metric": metric,
                    "company_value": round(
                        float(company_value),
                        2,
                    ),
                    "sector_median": round(
                        median,
                        2,
                    ),
                    "rank": rank_info["rank"],
                    "peer_count": rank_info["peer_count"],
                    "better_than_median": bool(
                        better_than_median
                    ),
                }
            )

        return pd.DataFrame(records)

    def quality_ranking(
        self,
        company_id,
        year="Mar 2024",
    ):
        """Return sector peers ranked by composite quality score."""

        peers = self.get_peers(
            company_id,
            year,
            include_company=True,
        )

        ranking = peers[
            [
                "company_id",
                "company_name",
                "broad_sector",
                "composite_quality_score",
            ]
        ].copy()

        ranking["composite_quality_score"] = (
            pd.to_numeric(
                ranking["composite_quality_score"],
                errors="coerce",
            )
        )

        ranking = ranking.sort_values(
            "composite_quality_score",
            ascending=False,
            na_position="last",
        ).reset_index(drop=True)

        ranking["rank"] = range(
            1,
            len(ranking) + 1,
        )

        return ranking[
            [
                "rank",
                "company_id",
                "company_name",
                "broad_sector",
                "composite_quality_score",
            ]
        ]


def main():
    print("=" * 60)
    print("Sprint 3 - Day 17")
    print("N100 Peer Comparison Engine")
    print("=" * 60)

    engine = PeerComparisonEngine()

    # Use TCS as the Day 17 validation company.
    company_id = "TCS"
    year = "Mar 2024"

    company = engine.get_company(
        company_id,
        year,
    )

    print(
        f"\nCompany: {company['company_name']}"
    )
    print(
        f"Sector : {company['broad_sector']}"
    )
    print(
        f"Year   : {year}"
    )

    peers = engine.get_peers(
        company_id,
        year,
    )

    print(
        f"\nSector peers: {len(peers)}"
    )

    print("\nPeer Comparison")
    print("-" * 60)

    comparison = engine.comparison_summary(
        company_id,
        year,
    )

    print(
        comparison.to_string(
            index=False
        )
    )

    print("\nSector Quality Ranking")
    print("-" * 60)

    ranking = engine.quality_ranking(
        company_id,
        year,
    )

    print(
        ranking.head(10).to_string(
            index=False
        )
    )

    print(
        "\nDay 17 peer comparison completed successfully."
    )


if __name__ == "__main__":
    main()