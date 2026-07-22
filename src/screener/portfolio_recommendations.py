"""
N100 Financial Intelligence Platform
Sprint 3 - Day 23
Portfolio Risk & Recommendation Engine

Generates analytical portfolio recommendations from the
Day 22 Portfolio Intelligence Engine.

These outputs are analytical model signals and are not
investment advice.
"""

from pathlib import Path
from typing import Iterable

import pandas as pd

from src.screener.portfolio_intelligence import (
    PortfolioIntelligenceEngine,
)


class PortfolioRecommendationEngine:
    """Generate portfolio-level and holding-level recommendations."""

    def __init__(self):
        self.portfolio_engine = PortfolioIntelligenceEngine()

    @staticmethod
    def _normalize_company_ids(
        company_ids: Iterable[str],
    ) -> list[str]:
        if company_ids is None:
            raise ValueError("Portfolio cannot be None.")

        normalized = []

        for company_id in company_ids:
            if company_id is None:
                continue

            value = str(company_id).strip().upper()

            if value and value not in normalized:
                normalized.append(value)

        if not normalized:
            raise ValueError("Portfolio cannot be empty.")

        return normalized

    @staticmethod
    def classify_action(
        signal: str,
        decision_score: float | None,
    ) -> str:
        """
        Convert analytical signal into a portfolio review action.
        """

        if decision_score is None or pd.isna(decision_score):
            return "Review"

        signal = str(signal).strip()

        if signal == "Strong Candidate":
            return "Maintain"

        if signal == "Candidate":
            return "Maintain"

        if signal == "Watch":
            return "Review"

        if signal == "Avoid":
            return "Reduce Exposure"

        return "Review"

    @staticmethod
    def classify_priority(
        signal: str,
        decision_score: float | None,
    ) -> str:
        """Determine recommendation priority."""

        if decision_score is None or pd.isna(decision_score):
            return "Medium"

        score = float(decision_score)
        signal = str(signal).strip()

        if signal == "Avoid" or score < 50:
            return "High"

        if signal == "Watch" or score < 65:
            return "Medium"

        return "Low"

    @staticmethod
    def recommendation_reason(row: pd.Series) -> str:
        """Create a concise reason for a holding recommendation."""

        signal = row.get("signal")
        score = row.get("decision_score")
        intelligence = row.get("intelligence_score")
        assessment = row.get("assessment")

        if signal == "Strong Candidate":
            return (
                "Strong analytical decision signal with "
                f"{intelligence:.2f}/100 company intelligence."
            )

        if signal == "Candidate":
            return (
                "Positive analytical candidate signal with "
                f"{score:.2f}/100 decision score."
            )

        if signal == "Watch":
            return (
                "Moderate analytical strength; fundamentals "
                "should be reviewed before increasing exposure."
            )

        if signal == "Avoid":
            return (
                "Weak analytical decision signal; review the "
                "holding and its identified fundamental risks."
            )

        return (
            f"Assessment is {assessment}; additional review "
            "is recommended."
        )

    def holding_recommendations(
        self,
        company_ids: Iterable[str],
        year: str,
        ignore_invalid: bool = False,
    ) -> pd.DataFrame:
        """Generate recommendation for every portfolio holding."""

        company_ids = self._normalize_company_ids(company_ids)

        portfolio = self.portfolio_engine.analyse_portfolio(
            company_ids,
            year,
            ignore_invalid=ignore_invalid,
        ).copy()

        portfolio["recommended_action"] = portfolio.apply(
            lambda row: self.classify_action(
                row.get("signal"),
                row.get("decision_score"),
            ),
            axis=1,
        )

        portfolio["priority"] = portfolio.apply(
            lambda row: self.classify_priority(
                row.get("signal"),
                row.get("decision_score"),
            ),
            axis=1,
        )

        portfolio["recommendation_reason"] = portfolio.apply(
            self.recommendation_reason,
            axis=1,
        )

        priority_order = {
            "High": 1,
            "Medium": 2,
            "Low": 3,
        }

        portfolio["_priority_order"] = (
            portfolio["priority"]
            .map(priority_order)
            .fillna(4)
        )

        portfolio = portfolio.sort_values(
            by=[
                "_priority_order",
                "decision_score",
            ],
            ascending=[
                True,
                True,
            ],
            na_position="last",
        ).reset_index(drop=True)

        portfolio["recommendation_rank"] = (
            range(1, len(portfolio) + 1)
        )

        portfolio = portfolio.drop(
            columns=["_priority_order"]
        )

        preferred_columns = [
            "recommendation_rank",
            "company_id",
            "company_name",
            "broad_sector",
            "year",
            "portfolio_weight_pct",
            "decision_score",
            "signal",
            "confidence",
            "intelligence_score",
            "assessment",
            "recommended_action",
            "priority",
            "recommendation_reason",
        ]

        available = [
            column
            for column in preferred_columns
            if column in portfolio.columns
        ]

        remaining = [
            column
            for column in portfolio.columns
            if column not in available
        ]

        return portfolio[
            available + remaining
        ].copy()

    def sector_risk_analysis(
        self,
        company_ids: Iterable[str],
        year: str,
        ignore_invalid: bool = False,
    ) -> pd.DataFrame:
        """Analyse sector concentration and classify sector risk."""

        company_ids = self._normalize_company_ids(company_ids)

        allocation = self.portfolio_engine.sector_allocation(
            company_ids,
            year,
            ignore_invalid=ignore_invalid,
        ).copy()

        def risk_level(weight):
            if weight >= 50:
                return "High"

            if weight >= 30:
                return "Moderate"

            return "Low"

        allocation["concentration_risk"] = (
            allocation["weight_pct"].apply(
                risk_level
            )
        )

        allocation["recommendation"] = allocation.apply(
            lambda row: (
                "Diversify sector exposure"
                if row["concentration_risk"] == "High"
                else (
                    "Monitor sector concentration"
                    if row["concentration_risk"]
                    == "Moderate"
                    else "Balanced exposure"
                )
            ),
            axis=1,
        )

        return allocation

    def action_distribution(
        self,
        company_ids: Iterable[str],
        year: str,
        ignore_invalid: bool = False,
    ) -> pd.DataFrame:
        """Return distribution of recommended holding actions."""

        recommendations = self.holding_recommendations(
            company_ids,
            year,
            ignore_invalid=ignore_invalid,
        )

        result = (
            recommendations
            .groupby(
                "recommended_action",
                dropna=False,
            )
            .size()
            .reset_index(
                name="company_count"
            )
        )

        total = result["company_count"].sum()

        result["weight_pct"] = (
            result["company_count"]
            / total
            * 100
        ).round(2)

        result = result.sort_values(
            by=[
                "company_count",
                "recommended_action",
            ],
            ascending=[
                False,
                True,
            ],
        ).reset_index(drop=True)

        return result

    def priority_distribution(
        self,
        company_ids: Iterable[str],
        year: str,
        ignore_invalid: bool = False,
    ) -> pd.DataFrame:
        """Return recommendation priority distribution."""

        recommendations = self.holding_recommendations(
            company_ids,
            year,
            ignore_invalid=ignore_invalid,
        )

        result = (
            recommendations
            .groupby(
                "priority",
                dropna=False,
            )
            .size()
            .reset_index(
                name="company_count"
            )
        )

        total = result["company_count"].sum()

        result["weight_pct"] = (
            result["company_count"]
            / total
            * 100
        ).round(2)

        priority_order = {
            "High": 1,
            "Medium": 2,
            "Low": 3,
        }

        result["_order"] = (
            result["priority"]
            .map(priority_order)
            .fillna(4)
        )

        result = result.sort_values(
            "_order"
        ).drop(
            columns="_order"
        ).reset_index(drop=True)

        return result

    def portfolio_recommendations(
        self,
        company_ids: Iterable[str],
        year: str,
        ignore_invalid: bool = False,
    ) -> list[str]:
        """Generate portfolio-level analytical recommendations."""

        summary = self.portfolio_engine.portfolio_summary(
            company_ids,
            year,
            ignore_invalid=ignore_invalid,
        )

        holdings = self.holding_recommendations(
            company_ids,
            year,
            ignore_invalid=ignore_invalid,
        )

        recommendations = []

        largest_weight = summary.get(
            "largest_sector_weight_pct",
            0,
        )

        largest_sector = summary.get(
            "largest_sector"
        )

        if largest_weight >= 50:
            recommendations.append(
                f"Diversify {largest_sector} exposure; "
                f"it represents {largest_weight:.1f}% "
                "of the portfolio."
            )

        avoid = holdings[
            holdings["signal"] == "Avoid"
        ]

        if not avoid.empty:
            names = ", ".join(
                avoid["company_name"].tolist()
            )

            recommendations.append(
                "Review or reduce exposure to holdings "
                f"with Avoid signals: {names}."
            )

        watch = holdings[
            holdings["signal"] == "Watch"
        ]

        if not watch.empty:
            names = ", ".join(
                watch["company_name"].tolist()
            )

            recommendations.append(
                "Closely monitor Watch holdings: "
                f"{names}."
            )

        strong = holdings[
            holdings["signal"]
            == "Strong Candidate"
        ]

        if not strong.empty:
            names = ", ".join(
                strong["company_name"].tolist()
            )

            recommendations.append(
                "Strong analytical holdings currently "
                f"include: {names}."
            )

        if (
            summary.get("diversification_score", 0)
            < 60
        ):
            recommendations.append(
                "Improve diversification across sectors "
                "to reduce concentration risk."
            )

        if not recommendations:
            recommendations.append(
                "No major portfolio-level analytical "
                "issues were detected."
            )

        return recommendations

    def recommendation_summary(
        self,
        company_ids: Iterable[str],
        year: str,
        ignore_invalid: bool = False,
    ) -> dict:
        """Build the Day 23 portfolio recommendation summary."""

        portfolio_summary = (
            self.portfolio_engine.portfolio_summary(
                company_ids,
                year,
                ignore_invalid=ignore_invalid,
            )
        )

        holdings = self.holding_recommendations(
            company_ids,
            year,
            ignore_invalid=ignore_invalid,
        )

        actions = self.action_distribution(
            company_ids,
            year,
            ignore_invalid=ignore_invalid,
        )

        priorities = self.priority_distribution(
            company_ids,
            year,
            ignore_invalid=ignore_invalid,
        )

        action_counts = dict(
            zip(
                actions["recommended_action"],
                actions["company_count"],
            )
        )

        priority_counts = dict(
            zip(
                priorities["priority"],
                priorities["company_count"],
            )
        )

        high_priority = holdings[
            holdings["priority"] == "High"
        ]

        return {
            "year": year,
            "company_count": len(holdings),
            "portfolio_score": portfolio_summary[
                "portfolio_score"
            ],
            "portfolio_health": portfolio_summary[
                "portfolio_health"
            ],
            "diversification_score": portfolio_summary[
                "diversification_score"
            ],
            "concentration_risk": portfolio_summary[
                "concentration_risk"
            ],
            "largest_sector": portfolio_summary[
                "largest_sector"
            ],
            "largest_sector_weight_pct": (
                portfolio_summary[
                    "largest_sector_weight_pct"
                ]
            ),
            "maintain_count": int(
                action_counts.get(
                    "Maintain",
                    0,
                )
            ),
            "review_count": int(
                action_counts.get(
                    "Review",
                    0,
                )
            ),
            "reduce_exposure_count": int(
                action_counts.get(
                    "Reduce Exposure",
                    0,
                )
            ),
            "high_priority_count": int(
                priority_counts.get(
                    "High",
                    0,
                )
            ),
            "medium_priority_count": int(
                priority_counts.get(
                    "Medium",
                    0,
                )
            ),
            "low_priority_count": int(
                priority_counts.get(
                    "Low",
                    0,
                )
            ),
            "highest_priority_company": (
                high_priority.iloc[0][
                    "company_name"
                ]
                if not high_priority.empty
                else None
            ),
            "recommendations": (
                self.portfolio_recommendations(
                    company_ids,
                    year,
                    ignore_invalid=ignore_invalid,
                )
            ),
        }

    def generate_summary(
        self,
        company_ids: Iterable[str],
        year: str,
        ignore_invalid: bool = False,
    ) -> str:
        """Generate readable Day 23 narrative."""

        summary = self.recommendation_summary(
            company_ids,
            year,
            ignore_invalid=ignore_invalid,
        )

        return (
            f"The portfolio contains "
            f"{summary['company_count']} companies for "
            f"{summary['year']}. Its portfolio health is "
            f"{summary['portfolio_health']} with a score "
            f"of {summary['portfolio_score']}/100. "
            f"{summary['largest_sector']} represents "
            f"{summary['largest_sector_weight_pct']}% "
            "of portfolio exposure. "
            f"{summary['high_priority_count']} holding(s) "
            "require high-priority analytical review."
        )

    def export_csv(
        self,
        company_ids: Iterable[str],
        year: str,
        output_path=None,
        ignore_invalid: bool = False,
    ) -> Path:
        """Export holding recommendations to CSV."""

        df = self.holding_recommendations(
            company_ids,
            year,
            ignore_invalid=ignore_invalid,
        )

        if output_path is None:
            output_path = (
                Path("output")
                / "portfolio_recommendations.csv"
            )
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

        return output_path.resolve()


def main():
    print("=" * 74)
    print("Sprint 3 - Day 23")
    print("N100 Portfolio Risk & Recommendation Engine")
    print("=" * 74)

    portfolio = [
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

    engine = PortfolioRecommendationEngine()

    recommendations = engine.holding_recommendations(
        portfolio,
        year,
    )

    print(f"\nYear: {year}")
    print(
        f"Companies analysed: "
        f"{len(recommendations)}"
    )

    print("\nHolding Recommendations")
    print("-" * 74)

    display_columns = [
        "recommendation_rank",
        "company_id",
        "company_name",
        "decision_score",
        "signal",
        "recommended_action",
        "priority",
    ]

    print(
        recommendations[
            display_columns
        ].to_string(
            index=False
        )
    )

    print("\nSector Risk Analysis")
    print("-" * 74)

    sector_risk = engine.sector_risk_analysis(
        portfolio,
        year,
    )

    print(
        sector_risk.to_string(
            index=False
        )
    )

    print("\nPortfolio Recommendations")
    print("-" * 74)

    portfolio_actions = (
        engine.portfolio_recommendations(
            portfolio,
            year,
        )
    )

    for index, recommendation in enumerate(
        portfolio_actions,
        start=1,
    ):
        print(
            f"{index}. {recommendation}"
        )

    print("\nRecommendation Summary")
    print("-" * 74)

    summary = engine.recommendation_summary(
        portfolio,
        year,
    )

    for key, value in summary.items():
        if key != "recommendations":
            print(
                f"{key:32}: {value}"
            )

    print("\nNarrative")
    print("-" * 74)

    print(
        engine.generate_summary(
            portfolio,
            year,
        )
    )

    output_path = engine.export_csv(
        portfolio,
        year,
    )

    print("\nCSV generated:")
    print(output_path)

    print(
        "\nDay 23 portfolio risk and recommendation "
        "analysis completed successfully."
    )

    print(
        "\nNote: Recommendations are analytical model "
        "outputs, not investment advice."
    )


if __name__ == "__main__":
    main()