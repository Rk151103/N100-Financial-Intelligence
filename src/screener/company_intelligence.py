"""
src/screener/company_intelligence.py

N100 Financial Intelligence Platform
Sprint 3 - Day 19
Company Intelligence Engine

Combines:
- Multi-factor ranking
- Sector ranking
- Profitability
- Growth
- Leverage
- Cash-flow strength
- Business efficiency

Produces:
- Overall assessment
- Strengths
- Risks
- Company intelligence summary
"""

from pathlib import Path
import sqlite3

import pandas as pd

from src.screener.ranking import RankingEngine


BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "db" / "nifty100.db"


class CompanyIntelligenceEngine:

    def __init__(self, db_path=DB_PATH):
        self.db_path = Path(db_path)

        self.ranking_engine = RankingEngine(
            db_path=self.db_path
        )

    # =====================================================
    # Company Financial Data
    # =====================================================

    def load_company_data(
        self,
        company_id,
        year="Mar 2024",
    ):
        """
        Load financial information for one company/year.
        """

        company_id = str(
            company_id
        ).strip().upper()

        query = """
        SELECT
            f.company_id,
            c.company_name,
            s.broad_sector,
            f.year,

            f.net_profit_margin_pct,
            f.operating_profit_margin_pct,
            f.return_on_equity_pct,

            f.debt_to_equity,
            f.interest_coverage,
            f.asset_turnover,

            f.free_cash_flow_cr,
            f.cash_from_operations_cr,

            f.revenue_cagr_5yr,
            f.pat_cagr_5yr,
            f.eps_cagr_5yr,

            f.composite_quality_score

        FROM financial_ratios f

        JOIN companies c
            ON f.company_id = c.id

        LEFT JOIN sectors s
            ON f.company_id = s.company_id

        WHERE UPPER(f.company_id) = ?
          AND f.year = ?
        """

        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(
                query,
                conn,
                params=(
                    company_id,
                    year,
                ),
            )

        if df.empty:
            raise ValueError(
                f"Company '{company_id}' "
                f"not found for {year}."
            )

        return df.iloc[0]

    # =====================================================
    # Helper
    # =====================================================

    @staticmethod
    def _valid(value):
        return pd.notna(value)

    # =====================================================
    # Strength Detection
    # =====================================================

    def identify_strengths(self, row):
        """
        Identify positive fundamental characteristics.
        """

        strengths = []

        roe = row["return_on_equity_pct"]

        if self._valid(roe) and roe >= 20:
            strengths.append(
                "Strong return on equity"
            )

        opm = row["operating_profit_margin_pct"]

        if self._valid(opm) and opm >= 20:
            strengths.append(
                "Strong operating profitability"
            )

        revenue_growth = row["revenue_cagr_5yr"]

        if (
            self._valid(revenue_growth)
            and revenue_growth >= 10
        ):
            strengths.append(
                "Healthy revenue growth"
            )

        pat_growth = row["pat_cagr_5yr"]

        if (
            self._valid(pat_growth)
            and pat_growth >= 10
        ):
            strengths.append(
                "Healthy profit growth"
            )

        eps_growth = row["eps_cagr_5yr"]

        if (
            self._valid(eps_growth)
            and eps_growth >= 10
        ):
            strengths.append(
                "Healthy EPS growth"
            )

        debt = row["debt_to_equity"]
        sector = row["broad_sector"]

        if (
            sector != "Financials"
            and self._valid(debt)
            and debt <= 0.5
        ):
            strengths.append(
                "Conservative leverage"
            )

        icr = row["interest_coverage"]

        if self._valid(icr) and icr >= 5:
            strengths.append(
                "Strong interest coverage"
            )

        fcf = row["free_cash_flow_cr"]

        if self._valid(fcf) and fcf > 0:
            strengths.append(
                "Positive free cash flow"
            )

        asset_turnover = row["asset_turnover"]

        if (
            self._valid(asset_turnover)
            and asset_turnover >= 1
        ):
            strengths.append(
                "Efficient asset utilization"
            )

        return strengths

    # =====================================================
    # Risk Detection
    # =====================================================

    def identify_risks(self, row):
        """
        Identify potential fundamental weaknesses.
        """

        risks = []

        roe = row["return_on_equity_pct"]

        if self._valid(roe) and roe < 10:
            risks.append(
                "Low return on equity"
            )

        opm = row["operating_profit_margin_pct"]

        if self._valid(opm) and opm < 10:
            risks.append(
                "Weak operating margin"
            )

        revenue_growth = row["revenue_cagr_5yr"]

        if (
            self._valid(revenue_growth)
            and revenue_growth < 0
        ):
            risks.append(
                "Revenue contraction"
            )

        pat_growth = row["pat_cagr_5yr"]

        if (
            self._valid(pat_growth)
            and pat_growth < 0
        ):
            risks.append(
                "Profit contraction"
            )

        eps_growth = row["eps_cagr_5yr"]

        if (
            self._valid(eps_growth)
            and eps_growth < 0
        ):
            risks.append(
                "EPS contraction"
            )

        debt = row["debt_to_equity"]
        sector = row["broad_sector"]

        # Financial companies are intentionally exempt
        # from generic debt/equity risk thresholds.
        if (
            sector != "Financials"
            and self._valid(debt)
            and debt > 2
        ):
            risks.append(
                "High financial leverage"
            )

        icr = row["interest_coverage"]

        if (
            self._valid(icr)
            and icr > 0
            and icr < 2
        ):
            risks.append(
                "Weak interest coverage"
            )

        fcf = row["free_cash_flow_cr"]

        if self._valid(fcf) and fcf < 0:
            risks.append(
                "Negative free cash flow"
            )

        asset_turnover = row["asset_turnover"]

        if (
            self._valid(asset_turnover)
            and asset_turnover < 0.5
        ):
            risks.append(
                "Low asset utilization"
            )

        return risks

    # =====================================================
    # Assessment Classification
    # =====================================================

    @staticmethod
    def classify_score(final_score):
        """
        Convert final ranking score into an
        intelligence classification.
        """

        if final_score is None:
            return "Insufficient Data"

        if final_score >= 80:
            return "Strong"

        if final_score >= 65:
            return "Good"

        if final_score >= 50:
            return "Average"

        return "Weak"

    # =====================================================
    # Intelligence Score
    # =====================================================

    @staticmethod
    def calculate_intelligence_score(
        ranking_score,
        strengths,
        risks,
    ):
        """
        Adjust ranking score slightly based on
        detected strengths and risks.

        Maximum adjustment:
        +10 from strengths
        -10 from risks
        """

        if ranking_score is None:
            return None

        strength_bonus = min(
            len(strengths) * 1.5,
            10,
        )

        risk_penalty = min(
            len(risks) * 2,
            10,
        )

        score = (
            ranking_score
            + strength_bonus
            - risk_penalty
        )

        score = max(
            0,
            min(
                100,
                score,
            ),
        )

        return round(
            score,
            2,
        )

    # =====================================================
    # Company Intelligence
    # =====================================================

    def analyse_company(
        self,
        company_id,
        year="Mar 2024",
    ):
        """
        Generate complete intelligence assessment.
        """

        row = self.load_company_data(
            company_id,
            year,
        )

        ranking = (
            self.ranking_engine
            .get_company_rank(
                company_id,
                year,
            )
        )

        sector_ranking = (
            self.ranking_engine
            .sector_rank(
                company_id,
                year,
            )
        )

        strengths = self.identify_strengths(
            row
        )

        risks = self.identify_risks(
            row
        )

        ranking_score = ranking[
            "final_score"
        ]

        intelligence_score = (
            self.calculate_intelligence_score(
                ranking_score,
                strengths,
                risks,
            )
        )

        assessment = self.classify_score(
            intelligence_score
        )

        return {
            "company_id": row["company_id"],
            "company_name": row["company_name"],
            "broad_sector": row["broad_sector"],
            "year": row["year"],

            "overall_rank": ranking["rank"],
            "sector_rank": (
                sector_ranking["sector_rank"]
                if sector_ranking
                else None
            ),
            "sector_company_count": (
                sector_ranking[
                    "sector_company_count"
                ]
                if sector_ranking
                else None
            ),

            "ranking_score": ranking_score,
            "intelligence_score": (
                intelligence_score
            ),
            "assessment": assessment,

            "factor_scores": {
                "quality": ranking[
                    "quality_score"
                ],
                "growth": ranking[
                    "growth_score"
                ],
                "profitability": ranking[
                    "profitability_score"
                ],
                "financial_strength": ranking[
                    "financial_strength_score"
                ],
                "efficiency": ranking[
                    "efficiency_score"
                ],
            },

            "financial_metrics": {
                "roe_pct": row[
                    "return_on_equity_pct"
                ],
                "opm_pct": row[
                    "operating_profit_margin_pct"
                ],
                "debt_to_equity": row[
                    "debt_to_equity"
                ],
                "interest_coverage": row[
                    "interest_coverage"
                ],
                "asset_turnover": row[
                    "asset_turnover"
                ],
                "free_cash_flow_cr": row[
                    "free_cash_flow_cr"
                ],
                "revenue_cagr_5yr": row[
                    "revenue_cagr_5yr"
                ],
                "pat_cagr_5yr": row[
                    "pat_cagr_5yr"
                ],
                "eps_cagr_5yr": row[
                    "eps_cagr_5yr"
                ],
            },

            "strengths": strengths,
            "risks": risks,
        }

    # =====================================================
    # Human-readable Summary
    # =====================================================

    def generate_summary(
        self,
        company_id,
        year="Mar 2024",
    ):
        result = self.analyse_company(
            company_id,
            year,
        )

        company = result[
            "company_name"
        ].strip()

        score = result[
            "intelligence_score"
        ]

        assessment = result[
            "assessment"
        ]

        overall_rank = result[
            "overall_rank"
        ]

        sector_rank = result[
            "sector_rank"
        ]

        sector_count = result[
            "sector_company_count"
        ]

        summary = (
            f"{company} has an intelligence "
            f"score of {score}/100 and is "
            f"classified as {assessment}. "
            f"It ranks #{overall_rank} overall"
        )

        if sector_rank is not None:
            summary += (
                f" and #{sector_rank} among "
                f"{sector_count} companies in "
                f"the {result['broad_sector']} sector"
            )

        summary += "."

        return summary


def main():
    print("=" * 65)
    print("Sprint 3 - Day 19")
    print("N100 Company Intelligence Engine")
    print("=" * 65)

    engine = CompanyIntelligenceEngine()

    company_id = "TCS"
    year = "Mar 2024"

    result = engine.analyse_company(
        company_id,
        year,
    )

    print(
        f"\nCompany : "
        f"{result['company_name'].strip()}"
    )

    print(
        f"Sector  : "
        f"{result['broad_sector']}"
    )

    print(
        f"Year    : "
        f"{result['year']}"
    )

    print(
        f"\nOverall Rank : "
        f"#{result['overall_rank']}"
    )

    print(
        f"Sector Rank  : "
        f"#{result['sector_rank']} / "
        f"{result['sector_company_count']}"
    )

    print(
        f"Ranking Score      : "
        f"{result['ranking_score']}"
    )

    print(
        f"Intelligence Score : "
        f"{result['intelligence_score']}"
    )

    print(
        f"Assessment         : "
        f"{result['assessment']}"
    )

    print("\nFactor Scores")
    print("-" * 65)

    for key, value in (
        result["factor_scores"].items()
    ):
        print(
            f"{key:20}: {value}"
        )

    print("\nStrengths")
    print("-" * 65)

    if result["strengths"]:
        for strength in result["strengths"]:
            print(
                f"+ {strength}"
            )
    else:
        print(
            "No major strengths detected."
        )

    print("\nRisks")
    print("-" * 65)

    if result["risks"]:
        for risk in result["risks"]:
            print(
                f"- {risk}"
            )
    else:
        print(
            "No major fundamental risks detected."
        )

    print("\nSummary")
    print("-" * 65)

    print(
        engine.generate_summary(
            company_id,
            year,
        )
    )

    print(
        "\nDay 19 company intelligence "
        "analysis completed successfully."
    )


if __name__ == "__main__":
    main()