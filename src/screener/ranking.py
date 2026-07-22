"""
src/screener/ranking.py

N100 Financial Intelligence Platform
Sprint 3 - Day 18
Multi-Factor Ranking Engine
"""

from pathlib import Path
import sqlite3

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "db" / "nifty100.db"


class RankingEngine:
    """
    Multi-factor company ranking engine.

    Uses percentile-based scoring to reduce the influence
    of extreme raw financial values.
    """

    DEFAULT_WEIGHTS = {
        "quality": 0.25,
        "growth": 0.25,
        "profitability": 0.20,
        "financial_strength": 0.20,
        "efficiency": 0.10,
    }

    def __init__(self, db_path=DB_PATH, weights=None):
        self.db_path = Path(db_path)
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self._validate_weights()

    def _validate_weights(self):
        required = set(self.DEFAULT_WEIGHTS)

        if set(self.weights) != required:
            raise ValueError(
                "Weights must contain exactly: "
                + ", ".join(sorted(required))
            )

        if any(value < 0 for value in self.weights.values()):
            raise ValueError("Weights cannot be negative.")

        total = sum(self.weights.values())

        if abs(total - 1.0) > 1e-9:
            raise ValueError(
                f"Weights must sum to 1.0. Current total: {total}"
            )

    def load_data(self, year="Mar 2024"):
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
    def _numeric(df, column):
        return pd.to_numeric(
            df[column],
            errors="coerce",
        )

    @staticmethod
    def percentile_score(series, higher_is_better=True):
        """
        Convert raw values into percentile scores from 0 to 100.
        Missing values remain missing.
        """

        numeric = pd.to_numeric(
            series,
            errors="coerce",
        )

        if higher_is_better:
            ranks = numeric.rank(
                pct=True,
                method="average",
                ascending=True,
            )
        else:
            ranks = numeric.rank(
                pct=True,
                method="average",
                ascending=False,
            )

        return ranks * 100

    def calculate_factor_scores(self, df):
        df = df.copy()

        # -------------------------------------------------
        # Quality
        # -------------------------------------------------

        df["quality_score"] = self.percentile_score(
            self._numeric(
                df,
                "composite_quality_score",
            )
        )

        # -------------------------------------------------
        # Growth
        # -------------------------------------------------

        revenue_score = self.percentile_score(
            self._numeric(
                df,
                "revenue_cagr_5yr",
            )
        )

        pat_score = self.percentile_score(
            self._numeric(
                df,
                "pat_cagr_5yr",
            )
        )

        eps_score = self.percentile_score(
            self._numeric(
                df,
                "eps_cagr_5yr",
            )
        )

        df["growth_score"] = pd.concat(
            [
                revenue_score,
                pat_score,
                eps_score,
            ],
            axis=1,
        ).mean(
            axis=1,
            skipna=True,
        )

        # -------------------------------------------------
        # Profitability
        # -------------------------------------------------

        roe_score = self.percentile_score(
            self._numeric(
                df,
                "return_on_equity_pct",
            )
        )

        opm_score = self.percentile_score(
            self._numeric(
                df,
                "operating_profit_margin_pct",
            )
        )

        df["profitability_score"] = pd.concat(
            [
                roe_score,
                opm_score,
            ],
            axis=1,
        ).mean(
            axis=1,
            skipna=True,
        )

        # -------------------------------------------------
        # Financial Strength
        # -------------------------------------------------

        de_score = self.percentile_score(
            self._numeric(
                df,
                "debt_to_equity",
            ),
            higher_is_better=False,
        )

        icr_score = self.percentile_score(
            self._numeric(
                df,
                "interest_coverage",
            )
        )

        fcf_score = self.percentile_score(
            self._numeric(
                df,
                "free_cash_flow_cr",
            )
        )

        df["financial_strength_score"] = pd.concat(
            [
                de_score,
                icr_score,
                fcf_score,
            ],
            axis=1,
        ).mean(
            axis=1,
            skipna=True,
        )

        # -------------------------------------------------
        # Efficiency
        # -------------------------------------------------

        df["efficiency_score"] = self.percentile_score(
            self._numeric(
                df,
                "asset_turnover",
            )
        )

        return df

    def calculate_final_score(self, df):
        """
        Calculate weighted final score.

        Missing factor scores are handled using only the
        available factor weights for that company.
        """

        df = self.calculate_factor_scores(df)

        factor_columns = {
            "quality": "quality_score",
            "growth": "growth_score",
            "profitability": "profitability_score",
            "financial_strength": "financial_strength_score",
            "efficiency": "efficiency_score",
        }

        final_scores = []

        for _, row in df.iterrows():
            weighted_sum = 0.0
            available_weight = 0.0

            for factor, column in factor_columns.items():
                value = row[column]
                weight = self.weights[factor]

                if pd.notna(value):
                    weighted_sum += value * weight
                    available_weight += weight

            if available_weight == 0:
                final_scores.append(None)
            else:
                final_scores.append(
                    weighted_sum / available_weight
                )

        df["final_score"] = final_scores

        df["final_score"] = df[
            "final_score"
        ].round(2)

        return df

    def rank_companies(
        self,
        year="Mar 2024",
        sector=None,
        top_n=None,
    ):
        """
        Rank companies by multi-factor final score.
        """

        df = self.load_data(year)

        if sector is not None:
            df = df[
                df["broad_sector"] == sector
            ].copy()

        if df.empty:
            return df

        df = self.calculate_final_score(df)

        df = df.sort_values(
            "final_score",
            ascending=False,
            na_position="last",
        ).reset_index(drop=True)

        df["rank"] = range(
            1,
            len(df) + 1,
        )

        if top_n is not None:
            df = df.head(top_n).copy()

        return df

    def get_company_rank(
        self,
        company_id,
        year="Mar 2024",
    ):
        """
        Return overall ranking information for one company.
        """

        ranking = self.rank_companies(year)

        company_id = str(
            company_id
        ).strip().upper()

        company = ranking[
            ranking["company_id"]
            .astype(str)
            .str.upper()
            == company_id
        ]

        if company.empty:
            raise ValueError(
                f"Company '{company_id}' not found for {year}."
            )

        row = company.iloc[0]

        return {
            "company_id": row["company_id"],
            "company_name": row["company_name"],
            "broad_sector": row["broad_sector"],
            "year": row["year"],
            "rank": int(row["rank"]),
            "final_score": float(row["final_score"]),
            "quality_score": round(
                float(row["quality_score"]),
                2,
            )
            if pd.notna(row["quality_score"])
            else None,
            "growth_score": round(
                float(row["growth_score"]),
                2,
            )
            if pd.notna(row["growth_score"])
            else None,
            "profitability_score": round(
                float(row["profitability_score"]),
                2,
            )
            if pd.notna(row["profitability_score"])
            else None,
            "financial_strength_score": round(
                float(row["financial_strength_score"]),
                2,
            )
            if pd.notna(row["financial_strength_score"])
            else None,
            "efficiency_score": round(
                float(row["efficiency_score"]),
                2,
            )
            if pd.notna(row["efficiency_score"])
            else None,
        }

    def sector_rank(
        self,
        company_id,
        year="Mar 2024",
    ):
        """
        Return company rank within its broad sector.
        """

        company = self.get_company_rank(
            company_id,
            year,
        )

        sector = company["broad_sector"]

        ranking = self.rank_companies(
            year=year,
            sector=sector,
        )

        company_id = str(
            company_id
        ).strip().upper()

        row = ranking[
            ranking["company_id"]
            .astype(str)
            .str.upper()
            == company_id
        ]

        if row.empty:
            return None

        row = row.iloc[0]

        return {
            "company_id": company_id,
            "sector": sector,
            "sector_rank": int(row["rank"]),
            "sector_company_count": len(ranking),
            "final_score": float(
                row["final_score"]
            ),
        }


def main():
    print("=" * 65)
    print("Sprint 3 - Day 18")
    print("N100 Multi-Factor Ranking Engine")
    print("=" * 65)

    engine = RankingEngine()

    year = "Mar 2024"

    ranking = engine.rank_companies(
        year=year,
        top_n=20,
    )

    print(f"\nYear: {year}")
    print(
        f"Companies ranked: "
        f"{len(engine.load_data(year))}"
    )

    print("\nTop 20 Multi-Factor Rankings")
    print("-" * 65)

    display_columns = [
        "rank",
        "company_id",
        "company_name",
        "broad_sector",
        "quality_score",
        "growth_score",
        "profitability_score",
        "financial_strength_score",
        "efficiency_score",
        "final_score",
    ]

    print(
        ranking[
            display_columns
        ].to_string(
            index=False
        )
    )

    print("\nTCS Ranking")
    print("-" * 65)

    tcs = engine.get_company_rank(
        "TCS",
        year,
    )

    for key, value in tcs.items():
        print(f"{key}: {value}")

    print("\nTCS Sector Ranking")
    print("-" * 65)

    sector = engine.sector_rank(
        "TCS",
        year,
    )

    for key, value in sector.items():
        print(f"{key}: {value}")

    print(
        "\nDay 18 multi-factor ranking completed successfully."
    )


if __name__ == "__main__":
    main()