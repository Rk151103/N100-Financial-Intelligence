"""
src/screener/watchlist.py

N100 Financial Intelligence Platform
Sprint 3 - Day 20
Watchlist Intelligence Engine

Combines multiple Company Intelligence results into:
- Watchlist ranking
- Assessment distribution
- Sector exposure
- Strongest / weakest company
- Average intelligence score
- CSV export
"""

from pathlib import Path

import pandas as pd

from src.screener.company_intelligence import (
    CompanyIntelligenceEngine,
)


BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "db" / "nifty100.db"
OUTPUT_DIR = BASE_DIR / "output"


class WatchlistIntelligenceEngine:

    def __init__(self, db_path=DB_PATH):
        self.db_path = Path(db_path)

        self.company_engine = CompanyIntelligenceEngine(
            db_path=self.db_path
        )

    # =====================================================
    # Input Validation
    # =====================================================

    @staticmethod
    def normalize_company_ids(company_ids):
        """
        Clean, normalize and remove duplicate company IDs
        while preserving their original order.
        """

        if company_ids is None:
            raise ValueError(
                "Company list cannot be None."
            )

        normalized = []

        seen = set()

        for company_id in company_ids:
            company_id = str(
                company_id
            ).strip().upper()

            if not company_id:
                continue

            if company_id not in seen:
                normalized.append(company_id)
                seen.add(company_id)

        if not normalized:
            raise ValueError(
                "Watchlist must contain at least one company."
            )

        return normalized

    # =====================================================
    # Watchlist Analysis
    # =====================================================

    def analyse_watchlist(
        self,
        company_ids,
        year="Mar 2024",
        ignore_invalid=False,
    ):
        """
        Analyse multiple companies using the Day 19
        Company Intelligence Engine.
        """

        company_ids = self.normalize_company_ids(
            company_ids
        )

        rows = []
        invalid_companies = []

        for company_id in company_ids:

            try:
                result = (
                    self.company_engine
                    .analyse_company(
                        company_id,
                        year,
                    )
                )

            except ValueError:

                if ignore_invalid:
                    invalid_companies.append(
                        company_id
                    )
                    continue

                raise

            factor_scores = result[
                "factor_scores"
            ]

            financial_metrics = result[
                "financial_metrics"
            ]

            rows.append(
                {
                    "company_id":
                        result["company_id"],

                    "company_name":
                        result["company_name"].strip(),

                    "broad_sector":
                        result["broad_sector"],

                    "year":
                        result["year"],

                    "overall_rank":
                        result["overall_rank"],

                    "sector_rank":
                        result["sector_rank"],

                    "ranking_score":
                        result["ranking_score"],

                    "intelligence_score":
                        result["intelligence_score"],

                    "assessment":
                        result["assessment"],

                    "quality_score":
                        factor_scores["quality"],

                    "growth_score":
                        factor_scores["growth"],

                    "profitability_score":
                        factor_scores[
                            "profitability"
                        ],

                    "financial_strength_score":
                        factor_scores[
                            "financial_strength"
                        ],

                    "efficiency_score":
                        factor_scores["efficiency"],

                    "roe_pct":
                        financial_metrics["roe_pct"],

                    "debt_to_equity":
                        financial_metrics[
                            "debt_to_equity"
                        ],

                    "revenue_cagr_5yr":
                        financial_metrics[
                            "revenue_cagr_5yr"
                        ],

                    "pat_cagr_5yr":
                        financial_metrics[
                            "pat_cagr_5yr"
                        ],

                    "free_cash_flow_cr":
                        financial_metrics[
                            "free_cash_flow_cr"
                        ],

                    "strength_count":
                        len(result["strengths"]),

                    "risk_count":
                        len(result["risks"]),

                    "strengths":
                        "; ".join(
                            result["strengths"]
                        ),

                    "risks":
                        "; ".join(
                            result["risks"]
                        ),
                }
            )

        if not rows:
            raise ValueError(
                "No valid companies were available "
                "for watchlist analysis."
            )

        df = pd.DataFrame(rows)

        df = df.sort_values(
            by=[
                "intelligence_score",
                "ranking_score",
            ],
            ascending=[
                False,
                False,
            ],
            na_position="last",
        ).reset_index(
            drop=True
        )

        df.insert(
            0,
            "watchlist_rank",
            range(
                1,
                len(df) + 1,
            ),
        )

        df.attrs[
            "invalid_companies"
        ] = invalid_companies

        return df

    # =====================================================
    # Top Companies
    # =====================================================

    def top_companies(
        self,
        company_ids,
        year="Mar 2024",
        n=5,
    ):
        """
        Return the highest-ranked watchlist companies.
        """

        if n <= 0:
            raise ValueError(
                "n must be greater than zero."
            )

        df = self.analyse_watchlist(
            company_ids,
            year,
        )

        return df.head(n).copy()

    # =====================================================
    # Strongest / Weakest
    # =====================================================

    def strongest_company(
        self,
        company_ids,
        year="Mar 2024",
    ):
        df = self.analyse_watchlist(
            company_ids,
            year,
        )

        return df.iloc[0].to_dict()

    def weakest_company(
        self,
        company_ids,
        year="Mar 2024",
    ):
        df = self.analyse_watchlist(
            company_ids,
            year,
        )

        return df.iloc[-1].to_dict()

    # =====================================================
    # Sector Distribution
    # =====================================================

    def sector_distribution(
        self,
        company_ids,
        year="Mar 2024",
    ):
        """
        Count watchlist companies by broad sector.
        """

        df = self.analyse_watchlist(
            company_ids,
            year,
        )

        distribution = (
            df["broad_sector"]
            .fillna("Unknown")
            .value_counts()
            .rename_axis("broad_sector")
            .reset_index(name="company_count")
        )

        total = len(df)

        distribution[
            "weight_pct"
        ] = (
            distribution["company_count"]
            / total
            * 100
        ).round(2)

        return distribution

    # =====================================================
    # Assessment Distribution
    # =====================================================

    def assessment_distribution(
        self,
        company_ids,
        year="Mar 2024",
    ):
        """
        Count companies by intelligence assessment.
        """

        df = self.analyse_watchlist(
            company_ids,
            year,
        )

        result = (
            df["assessment"]
            .fillna("Unknown")
            .value_counts()
            .rename_axis("assessment")
            .reset_index(name="company_count")
        )

        result[
            "weight_pct"
        ] = (
            result["company_count"]
            / len(df)
            * 100
        ).round(2)

        return result

    # =====================================================
    # Watchlist Summary
    # =====================================================

    def summary(
        self,
        company_ids,
        year="Mar 2024",
        ignore_invalid=False,
    ):
        """
        Produce aggregate watchlist intelligence.
        """

        df = self.analyse_watchlist(
            company_ids,
            year,
            ignore_invalid=ignore_invalid,
        )

        strongest = df.iloc[0]
        weakest = df.iloc[-1]

        sector_counts = (
            df["broad_sector"]
            .fillna("Unknown")
            .value_counts()
        )

        largest_sector = (
            sector_counts.index[0]
            if not sector_counts.empty
            else None
        )

        return {
            "year": year,

            "company_count": len(df),

            "average_intelligence_score": round(
                df[
                    "intelligence_score"
                ].mean(),
                2,
            ),

            "average_ranking_score": round(
                df[
                    "ranking_score"
                ].mean(),
                2,
            ),

            "strongest_company_id":
                strongest["company_id"],

            "strongest_company_name":
                strongest["company_name"],

            "strongest_score": round(
                strongest[
                    "intelligence_score"
                ],
                2,
            ),

            "weakest_company_id":
                weakest["company_id"],

            "weakest_company_name":
                weakest["company_name"],

            "weakest_score": round(
                weakest[
                    "intelligence_score"
                ],
                2,
            ),

            "sector_count":
                df["broad_sector"].nunique(
                    dropna=False
                ),

            "largest_sector":
                largest_sector,

            "strong_count": int(
                (
                    df["assessment"]
                    == "Strong"
                ).sum()
            ),

            "good_count": int(
                (
                    df["assessment"]
                    == "Good"
                ).sum()
            ),

            "average_count": int(
                (
                    df["assessment"]
                    == "Average"
                ).sum()
            ),

            "weak_count": int(
                (
                    df["assessment"]
                    == "Weak"
                ).sum()
            ),

            "invalid_companies":
                df.attrs.get(
                    "invalid_companies",
                    [],
                ),
        }

    # =====================================================
    # CSV Export
    # =====================================================

    def export_csv(
        self,
        company_ids,
        year="Mar 2024",
        output_path=None,
    ):
        """
        Export ranked watchlist intelligence to CSV.
        """

        df = self.analyse_watchlist(
            company_ids,
            year,
        )

        if output_path is None:
            OUTPUT_DIR.mkdir(
                parents=True,
                exist_ok=True,
            )

            output_path = (
                OUTPUT_DIR
                / "watchlist_intelligence.csv"
            )

        else:
            output_path = Path(
                output_path
            )

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

        df.to_csv(
            output_path,
            index=False,
        )

        return output_path

    # =====================================================
    # Human-readable Summary
    # =====================================================

    def generate_summary(
        self,
        company_ids,
        year="Mar 2024",
    ):
        result = self.summary(
            company_ids,
            year,
        )

        return (
            f"The watchlist contains "
            f"{result['company_count']} companies "
            f"across {result['sector_count']} sectors "
            f"for {year}. "
            f"The average intelligence score is "
            f"{result['average_intelligence_score']}/100. "
            f"{result['strongest_company_name']} is the "
            f"highest-ranked watchlist company with a "
            f"score of {result['strongest_score']}/100, "
            f"while {result['weakest_company_name']} "
            f"has the lowest score at "
            f"{result['weakest_score']}/100."
        )


def main():

    print("=" * 70)
    print("Sprint 3 - Day 20")
    print("N100 Watchlist Intelligence Engine")
    print("=" * 70)

    engine = WatchlistIntelligenceEngine()

    watchlist = [
        "TCS",
        "INFY",
        "HCLTECH",
        "LTIM",
        "RELIANCE",
        "ITC",
        "MARUTI",
        "HAL",
    ]

    year = "Mar 2024"

    results = engine.analyse_watchlist(
        watchlist,
        year,
    )

    print(
        f"\nYear: {year}"
    )

    print(
        f"Companies analysed: "
        f"{len(results)}"
    )

    print(
        "\nWatchlist Ranking"
    )

    print("-" * 70)

    columns = [
        "watchlist_rank",
        "company_id",
        "company_name",
        "broad_sector",
        "intelligence_score",
        "assessment",
        "overall_rank",
    ]

    print(
        results[
            columns
        ].to_string(
            index=False
        )
    )

    print(
        "\nSector Distribution"
    )

    print("-" * 70)

    print(
        engine.sector_distribution(
            watchlist,
            year,
        ).to_string(
            index=False
        )
    )

    print(
        "\nAssessment Distribution"
    )

    print("-" * 70)

    print(
        engine.assessment_distribution(
            watchlist,
            year,
        ).to_string(
            index=False
        )
    )

    print(
        "\nWatchlist Summary"
    )

    print("-" * 70)

    summary = engine.summary(
        watchlist,
        year,
    )

    for key, value in summary.items():
        print(
            f"{key:28}: {value}"
        )

    print(
        "\nNarrative"
    )

    print("-" * 70)

    print(
        engine.generate_summary(
            watchlist,
            year,
        )
    )

    output_path = engine.export_csv(
        watchlist,
        year,
    )

    print(
        f"\nCSV generated:\n"
        f"{output_path}"
    )

    print(
        "\nDay 20 watchlist intelligence "
        "analysis completed successfully."
    )


if __name__ == "__main__":
    main()