"""
src/analytics/peer_comparison.py

N100 Financial Intelligence Platform
Sprint 3 - Day 17
Peer Comparison Engine
"""

import sqlite3
from pathlib import Path

import pandas as pd


class PeerComparisonEngine:
    """
    Compare a company with all companies in the same sector.
    """

    def __init__(self, db_path="db/nifty100.db"):
        self.db_path = Path(db_path)

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def load_data(self, year="Mar 2024"):
        """
        Load company financial data.
        """

        query = """
        SELECT
            c.id AS company_id,
            c.company_name,
            s.broad_sector,
            fr.return_on_equity_pct,
            fr.operating_profit_margin_pct,
            fr.revenue_cagr_5yr,
            fr.pat_cagr_5yr,
            fr.eps_cagr_5yr,
            fr.debt_to_equity,
            fr.composite_quality_score
        FROM companies c
        LEFT JOIN sectors s
            ON c.id = s.company_id
        LEFT JOIN financial_ratios fr
            ON c.id = fr.company_id
        WHERE fr.year = ?
        """

        with self._connect() as conn:
            df = pd.read_sql_query(
                query,
                conn,
                params=[year]
            )

        return df

    def compare(self, company_name, year="Mar 2024"):
        """
        Compare one company with its peers.
        """

        df = self.load_data(year)

        company = df[
            df["company_name"].str.lower() ==
            company_name.lower()
        ]

        if company.empty:
            raise ValueError(
                f"Company '{company_name}' not found."
            )

        sector = company.iloc[0]["broad_sector"]

        peers = (
            df[df["broad_sector"] == sector]
            .copy()
        )

        ranking_columns = [
            "return_on_equity_pct",
            "operating_profit_margin_pct",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "eps_cagr_5yr",
            "composite_quality_score",
        ]

        for column in ranking_columns:

            peers[column] = pd.to_numeric(
                peers[column],
                errors="coerce"
            )

            peers[f"{column}_rank"] = (
                peers[column]
                .rank(
                    ascending=False,
                    method="min",
                    na_option="bottom"
                )
                .astype("Int64")
            )

        peers = peers.sort_values(
            by="composite_quality_score",
            ascending=False,
            na_position="last"
        )

        peers.reset_index(
            drop=True,
            inplace=True
        )

        return peers

    def export_csv(
        self,
        company_name,
        output_path="output/peer_comparison.csv",
        year="Mar 2024",
    ):
        """
        Export peer comparison.
        """

        peers = self.compare(
            company_name,
            year
        )

        Path(output_path).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        peers.to_csv(
            output_path,
            index=False
        )

        return output_path


def main():

    print("=" * 65)
    print("Sprint 3 - Day 17")
    print("Peer Comparison Engine")
    print("=" * 65)

    engine = PeerComparisonEngine()

    company = "ICICI Bank Ltd"

    peers = engine.compare(company)

    print(f"\nCompany : {company}")
    print(f"Sector  : {peers.iloc[0]['broad_sector']}")
    print(f"Peers   : {len(peers)}")

    print("\nTop 10 Peer Comparison")
    print("-" * 65)

    columns = [
        "company_name",
        "return_on_equity_pct",
        "return_on_equity_pct_rank",
        "operating_profit_margin_pct",
        "operating_profit_margin_pct_rank",
        "revenue_cagr_5yr",
        "revenue_cagr_5yr_rank",
        "pat_cagr_5yr",
        "pat_cagr_5yr_rank",
        "eps_cagr_5yr",
        "eps_cagr_5yr_rank",
        "composite_quality_score",
        "composite_quality_score_rank",
    ]

    available_columns = [
        column
        for column in columns
        if column in peers.columns
    ]

    print(
        peers[available_columns]
        .head(10)
        .to_string(index=False)
    )

    output = engine.export_csv(company)

    print(f"\nCSV exported to : {output}")

    print("\nPeer Comparison completed successfully.")


if __name__ == "__main__":
    main()