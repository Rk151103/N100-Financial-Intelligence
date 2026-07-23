"""
Sprint 3 - Day 24
N100 Financial Intelligence Platform

Portfolio Intelligence Report Generator

Combines:
- Portfolio Intelligence
- Decision Signals
- Portfolio Risk & Recommendations
- Sector Allocation
- Holding-Level Intelligence

Outputs a consolidated portfolio intelligence report.
"""

from pathlib import Path
from typing import Iterable, Optional, Union

import pandas as pd

from src.screener.portfolio_intelligence import PortfolioIntelligenceEngine
from src.screener.portfolio_recommendations import PortfolioRecommendationEngine


DEFAULT_PORTFOLIO = [
    "TCS",
    "INFY",
    "HCLTECH",
    "LTIM",
    "RELIANCE",
    "ITC",
    "MARUTI",
    "HAL",
]

DEFAULT_YEAR = "Mar 2024"


class PortfolioReportGenerator:
    """
    Generate consolidated portfolio intelligence reports.
    """

    def __init__(self):
        self.portfolio_engine = PortfolioIntelligenceEngine()
        self.recommendation_engine = PortfolioRecommendationEngine()

    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    @staticmethod
    def _normalize_company_ids(
        company_ids: Iterable[str],
    ) -> list[str]:

        if company_ids is None:
            raise ValueError("Portfolio cannot be None.")

        normalized = []
        seen = set()

        for company_id in company_ids:
            if company_id is None:
                continue

            company_id = str(company_id).strip().upper()

            if not company_id:
                continue

            if company_id not in seen:
                normalized.append(company_id)
                seen.add(company_id)

        if not normalized:
            raise ValueError(
                "Portfolio must contain at least one company."
            )

        return normalized

    @staticmethod
    def _safe_value(value, default=None):
        if value is None:
            return default

        try:
            if pd.isna(value):
                return default
        except (TypeError, ValueError):
            pass

        return value

    # --------------------------------------------------------
    # Holding Report
    # --------------------------------------------------------

    def holding_report(
        self,
        company_ids: Iterable[str],
        year: str = DEFAULT_YEAR,
        ignore_invalid: bool = False,
    ) -> pd.DataFrame:
        """
        Generate consolidated holding-level intelligence.
        """

        company_ids = self._normalize_company_ids(
            company_ids
        )

        portfolio = self.portfolio_engine.analyse_portfolio(
            company_ids,
            year,
            ignore_invalid=ignore_invalid,
        )

        recommendations = (
            self.recommendation_engine
            .holding_recommendations(
                company_ids,
                year,
                ignore_invalid=ignore_invalid,
            )
        )

        recommendation_columns = [
            "company_id",
            "recommendation_rank",
            "recommended_action",
            "priority",
            "recommendation_reason",
        ]

        available_columns = [
            column
            for column in recommendation_columns
            if column in recommendations.columns
        ]

        merged = portfolio.merge(
            recommendations[available_columns],
            on="company_id",
            how="left",
        )

        preferred_columns = [
            "company_id",
            "company_name",
            "broad_sector",
            "year",
            "overall_rank",
            "sector_rank",
            "ranking_score",
            "intelligence_score",
            "assessment",
            "decision_score",
            "signal",
            "confidence",
            "recommended_action",
            "priority",
            "recommendation_rank",
            "strength_count",
            "risk_count",
            "portfolio_weight_pct",
            "reasons",
            "recommendation_reason",
        ]

        existing_columns = [
            column
            for column in preferred_columns
            if column in merged.columns
        ]

        remaining_columns = [
            column
            for column in merged.columns
            if column not in existing_columns
        ]

        merged = merged[
            existing_columns + remaining_columns
        ].copy()

        if "decision_score" in merged.columns:
            merged = merged.sort_values(
                by="decision_score",
                ascending=False,
                na_position="last",
            )

        merged = merged.reset_index(drop=True)

        merged.insert(
            0,
            "report_rank",
            range(1, len(merged) + 1),
        )

        return merged

    # --------------------------------------------------------
    # Sector Report
    # --------------------------------------------------------

    def sector_report(
        self,
        company_ids: Iterable[str],
        year: str = DEFAULT_YEAR,
        ignore_invalid: bool = False,
    ) -> pd.DataFrame:

        company_ids = self._normalize_company_ids(
            company_ids
        )

        allocation = (
            self.portfolio_engine
            .sector_allocation(
                company_ids,
                year,
                ignore_invalid=ignore_invalid,
            )
        )

        sector_risk = (
            self.recommendation_engine
            .sector_risk_analysis(
                company_ids,
                year,
                ignore_invalid=ignore_invalid,
            )
        )

        risk_columns = [
            "broad_sector",
            "concentration_risk",
            "recommendation",
        ]

        available = [
            column
            for column in risk_columns
            if column in sector_risk.columns
        ]

        result = allocation.merge(
            sector_risk[available],
            on="broad_sector",
            how="left",
        )

        result = result.sort_values(
            by="weight_pct",
            ascending=False,
        ).reset_index(drop=True)

        return result

    # --------------------------------------------------------
    # Executive Summary
    # --------------------------------------------------------

    def executive_summary(
        self,
        company_ids: Iterable[str],
        year: str = DEFAULT_YEAR,
        ignore_invalid: bool = False,
    ) -> dict:

        company_ids = self._normalize_company_ids(
            company_ids
        )

        portfolio_summary = (
            self.portfolio_engine
            .portfolio_summary(
                company_ids,
                year,
                ignore_invalid=ignore_invalid,
            )
        )

        recommendation_summary = (
            self.recommendation_engine
            .recommendation_summary(
                company_ids,
                year,
                ignore_invalid=ignore_invalid,
            )
        )

        holdings = self.holding_report(
            company_ids,
            year,
            ignore_invalid=ignore_invalid,
        )

        strongest = holdings.iloc[0]
        weakest = holdings.iloc[-1]

        summary = {
            "year": year,
            "company_count": int(len(holdings)),
            "sector_count": portfolio_summary.get(
                "sector_count"
            ),
            "portfolio_score": portfolio_summary.get(
                "portfolio_score"
            ),
            "portfolio_health": portfolio_summary.get(
                "portfolio_health"
            ),
            "average_intelligence_score":
                portfolio_summary.get(
                    "average_intelligence_score"
                ),
            "average_decision_score":
                portfolio_summary.get(
                    "average_decision_score"
                ),
            "diversification_score":
                portfolio_summary.get(
                    "diversification_score"
                ),
            "concentration_risk":
                portfolio_summary.get(
                    "concentration_risk"
                ),
            "largest_sector":
                portfolio_summary.get(
                    "largest_sector"
                ),
            "largest_sector_weight_pct":
                portfolio_summary.get(
                    "largest_sector_weight_pct"
                ),
            "strongest_company_id":
                strongest["company_id"],
            "strongest_company_name":
                strongest["company_name"],
            "strongest_decision_score":
                self._safe_value(
                    strongest.get("decision_score")
                ),
            "weakest_company_id":
                weakest["company_id"],
            "weakest_company_name":
                weakest["company_name"],
            "weakest_decision_score":
                self._safe_value(
                    weakest.get("decision_score")
                ),
            "maintain_count":
                recommendation_summary.get(
                    "maintain_count",
                    0,
                ),
            "review_count":
                recommendation_summary.get(
                    "review_count",
                    0,
                ),
            "reduce_exposure_count":
                recommendation_summary.get(
                    "reduce_exposure_count",
                    0,
                ),
            "high_priority_count":
                recommendation_summary.get(
                    "high_priority_count",
                    0,
                ),
            "medium_priority_count":
                recommendation_summary.get(
                    "medium_priority_count",
                    0,
                ),
            "low_priority_count":
                recommendation_summary.get(
                    "low_priority_count",
                    0,
                ),
        }

        return summary

    # --------------------------------------------------------
    # Portfolio Recommendations
    # --------------------------------------------------------

    def recommendations(
        self,
        company_ids: Iterable[str],
        year: str = DEFAULT_YEAR,
        ignore_invalid: bool = False,
    ) -> list[str]:

        return (
            self.recommendation_engine
            .portfolio_recommendations(
                company_ids,
                year,
                ignore_invalid=ignore_invalid,
            )
        )

    # --------------------------------------------------------
    # Narrative
    # --------------------------------------------------------

    def generate_narrative(
        self,
        company_ids: Iterable[str],
        year: str = DEFAULT_YEAR,
        ignore_invalid: bool = False,
    ) -> str:

        summary = self.executive_summary(
            company_ids,
            year,
            ignore_invalid=ignore_invalid,
        )

        company_count = summary["company_count"]
        sector_count = summary["sector_count"]
        score = summary["portfolio_score"]
        health = summary["portfolio_health"]

        diversification = summary[
            "diversification_score"
        ]

        concentration = summary[
            "concentration_risk"
        ]

        largest_sector = summary[
            "largest_sector"
        ]

        largest_weight = summary[
            "largest_sector_weight_pct"
        ]

        strongest = summary[
            "strongest_company_name"
        ]

        weakest = summary[
            "weakest_company_name"
        ]

        high_priority = summary[
            "high_priority_count"
        ]

        return (
            f"The portfolio contains {company_count} companies "
            f"across {sector_count} sectors for {year}. "
            f"Its portfolio intelligence score is "
            f"{score}/100 and is classified as {health}. "
            f"The diversification score is "
            f"{diversification}/100 with "
            f"{str(concentration).lower()} concentration risk. "
            f"{largest_sector} is the largest sector exposure "
            f"at {largest_weight}%. "
            f"{strongest} is the strongest holding based on "
            f"the analytical decision score, while {weakest} "
            f"is the weakest. "
            f"{high_priority} holding(s) currently require "
            f"high-priority analytical review."
        )

    # --------------------------------------------------------
    # Complete Report
    # --------------------------------------------------------

    def generate_report(
        self,
        company_ids: Iterable[str],
        year: str = DEFAULT_YEAR,
        ignore_invalid: bool = False,
    ) -> dict:
        """
        Generate all report components.
        """

        company_ids = self._normalize_company_ids(
            company_ids
        )

        return {
            "summary": self.executive_summary(
                company_ids,
                year,
                ignore_invalid=ignore_invalid,
            ),
            "holdings": self.holding_report(
                company_ids,
                year,
                ignore_invalid=ignore_invalid,
            ),
            "sectors": self.sector_report(
                company_ids,
                year,
                ignore_invalid=ignore_invalid,
            ),
            "recommendations": self.recommendations(
                company_ids,
                year,
                ignore_invalid=ignore_invalid,
            ),
            "narrative": self.generate_narrative(
                company_ids,
                year,
                ignore_invalid=ignore_invalid,
            ),
        }

    # --------------------------------------------------------
    # CSV Export
    # --------------------------------------------------------

    def export_csv(
        self,
        company_ids: Iterable[str],
        year: str = DEFAULT_YEAR,
        output_path: Optional[
            Union[str, Path]
        ] = None,
        ignore_invalid: bool = False,
    ) -> Path:

        holdings = self.holding_report(
            company_ids,
            year,
            ignore_invalid=ignore_invalid,
        )

        if output_path is None:
            project_root = Path(__file__).resolve().parents[2]

            output_path = (
                project_root
                / "output"
                / "portfolio_intelligence_report.csv"
            )
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        holdings.to_csv(
            output_path,
            index=False,
        )

        return output_path


def main():

    print("=" * 76)
    print("Sprint 3 - Day 24")
    print("N100 Portfolio Intelligence Report Generator")
    print("=" * 76)

    generator = PortfolioReportGenerator()

    report = generator.generate_report(
        DEFAULT_PORTFOLIO,
        DEFAULT_YEAR,
    )

    summary = report["summary"]
    holdings = report["holdings"]
    sectors = report["sectors"]
    recommendations = report[
        "recommendations"
    ]

    print()
    print(f"Year: {DEFAULT_YEAR}")
    print(
        f"Companies analysed: "
        f"{summary['company_count']}"
    )

    print()
    print("Executive Summary")
    print("-" * 76)

    for key, value in summary.items():
        print(f"{key:<32}: {value}")

    print()
    print("Portfolio Holdings")
    print("-" * 76)

    display_columns = [
        "report_rank",
        "company_id",
        "company_name",
        "broad_sector",
        "decision_score",
        "signal",
        "recommended_action",
        "priority",
        "portfolio_weight_pct",
    ]

    display_columns = [
        column
        for column in display_columns
        if column in holdings.columns
    ]

    print(
        holdings[
            display_columns
        ].to_string(index=False)
    )

    print()
    print("Sector Intelligence")
    print("-" * 76)
    print(
        sectors.to_string(
            index=False
        )
    )

    print()
    print("Portfolio Recommendations")
    print("-" * 76)

    for index, recommendation in enumerate(
        recommendations,
        start=1,
    ):
        print(
            f"{index}. {recommendation}"
        )

    print()
    print("Portfolio Narrative")
    print("-" * 76)
    print(report["narrative"])

    output_path = generator.export_csv(
        DEFAULT_PORTFOLIO,
        DEFAULT_YEAR,
    )

    print()
    print("CSV generated:")
    print(output_path)

    print()
    print(
        "Day 24 portfolio intelligence report "
        "generated successfully."
    )

    print()
    print(
        "Note: Report outputs are analytical model "
        "results, not investment advice."
    )


if __name__ == "__main__":
    main()