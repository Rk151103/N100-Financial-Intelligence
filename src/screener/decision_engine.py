"""
src/screener/decision_engine.py

N100 Financial Intelligence Platform
Sprint 3 - Day 21
Decision Signal Engine

Produces analytical decision signals from the existing
ranking and company-intelligence layers.

Signals:
- Strong Candidate
- Candidate
- Watch
- Avoid
- Insufficient Data

These signals are analytical classifications and are not
investment advice.
"""

from pathlib import Path

import pandas as pd

from src.screener.company_intelligence import CompanyIntelligenceEngine


BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "db" / "nifty100.db"
OUTPUT_DIR = BASE_DIR / "output"


class DecisionSignalEngine:
    """Generate explainable analytical signals for N100 companies."""

    SIGNAL_ORDER = {
        "Strong Candidate": 5,
        "Candidate": 4,
        "Watch": 3,
        "Avoid": 2,
        "Insufficient Data": 1,
    }

    def __init__(self, db_path=DB_PATH):
        self.db_path = Path(db_path)

        self.company_engine = CompanyIntelligenceEngine(
            db_path=self.db_path
        )

    # =========================================================
    # Score Helpers
    # =========================================================

    @staticmethod
    def _safe_float(value):
        """Convert a value to float when possible."""

        if value is None:
            return None

        try:
            value = float(value)
        except (TypeError, ValueError):
            return None

        if pd.isna(value):
            return None

        return value

    @staticmethod
    def _clamp(value, minimum=0.0, maximum=100.0):
        return max(
            minimum,
            min(maximum, value),
        )

    # =========================================================
    # Decision Score
    # =========================================================

    def calculate_decision_score(self, analysis):
        """
        Calculate a 0-100 decision score.

        Weighting:
        Intelligence score     40%
        Ranking score          25%
        Quality                10%
        Profitability          10%
        Financial strength     10%
        Growth                  5%

        Risk penalties are applied afterwards.
        """

        intelligence_score = self._safe_float(
            analysis.get("intelligence_score")
        )

        ranking_score = self._safe_float(
            analysis.get("ranking_score")
        )

        factor_scores = analysis.get(
            "factor_scores",
            {},
        )

        quality = self._safe_float(
            factor_scores.get("quality")
        )

        profitability = self._safe_float(
            factor_scores.get("profitability")
        )

        financial_strength = self._safe_float(
            factor_scores.get("financial_strength")
        )

        growth = self._safe_float(
            factor_scores.get("growth")
        )

        weighted_values = [
            (intelligence_score, 0.40),
            (ranking_score, 0.25),
            (quality, 0.10),
            (profitability, 0.10),
            (financial_strength, 0.10),
            (growth, 0.05),
        ]

        available = [
            (value, weight)
            for value, weight in weighted_values
            if value is not None
        ]

        if not available:
            return None

        available_weight = sum(
            weight
            for _, weight in available
        )

        if available_weight == 0:
            return None

        score = sum(
            value * weight
            for value, weight in available
        ) / available_weight

        risks = analysis.get(
            "risks",
            [],
        ) or []

        # Each detected fundamental risk reduces the
        # decision score by 2 points, capped at 10.
        risk_penalty = min(
            len(risks) * 2.0,
            10.0,
        )

        score -= risk_penalty

        return round(
            self._clamp(score),
            2,
        )

    # =========================================================
    # Signal Classification
    # =========================================================

    @staticmethod
    def classify_signal(score):
        """Convert decision score into an analytical signal."""

        if score is None:
            return "Insufficient Data"

        if score >= 80:
            return "Strong Candidate"

        if score >= 65:
            return "Candidate"

        if score >= 50:
            return "Watch"

        return "Avoid"

    # =========================================================
    # Confidence
    # =========================================================

    @staticmethod
    def calculate_confidence(analysis):
        """
        Estimate signal confidence from factor availability.
        """

        factor_scores = analysis.get(
            "factor_scores",
            {},
        )

        required_values = [
            analysis.get("intelligence_score"),
            analysis.get("ranking_score"),
            factor_scores.get("quality"),
            factor_scores.get("growth"),
            factor_scores.get("profitability"),
            factor_scores.get("financial_strength"),
            factor_scores.get("efficiency"),
        ]

        available = 0

        for value in required_values:
            if value is None:
                continue

            try:
                if not pd.isna(float(value)):
                    available += 1
            except (TypeError, ValueError):
                continue

        ratio = available / len(required_values)

        if ratio >= 0.85:
            return "High"

        if ratio >= 0.60:
            return "Medium"

        return "Low"

    # =========================================================
    # Reason Generation
    # =========================================================

    @staticmethod
    def generate_reasons(analysis):
        """Generate human-readable reasons for the signal."""

        reasons = []

        intelligence = analysis.get(
            "intelligence_score"
        )

        ranking = analysis.get(
            "ranking_score"
        )

        factor_scores = analysis.get(
            "factor_scores",
            {},
        )

        if intelligence is not None:
            if intelligence >= 80:
                reasons.append(
                    "Strong overall company intelligence"
                )
            elif intelligence >= 65:
                reasons.append(
                    "Good overall company intelligence"
                )
            elif intelligence < 50:
                reasons.append(
                    "Weak overall company intelligence"
                )

        if ranking is not None:
            if ranking >= 75:
                reasons.append(
                    "Strong multi-factor ranking score"
                )
            elif ranking < 50:
                reasons.append(
                    "Below-average multi-factor ranking score"
                )

        quality = factor_scores.get("quality")

        if quality is not None and quality >= 75:
            reasons.append(
                "Strong quality factor"
            )

        profitability = factor_scores.get(
            "profitability"
        )

        if (
            profitability is not None
            and profitability >= 75
        ):
            reasons.append(
                "Strong profitability factor"
            )

        financial_strength = factor_scores.get(
            "financial_strength"
        )

        if (
            financial_strength is not None
            and financial_strength >= 75
        ):
            reasons.append(
                "Strong financial strength"
            )

        growth = factor_scores.get("growth")

        if growth is not None:
            if growth >= 75:
                reasons.append(
                    "Strong growth factor"
                )
            elif growth < 40:
                reasons.append(
                    "Growth factor is relatively weak"
                )

        risks = analysis.get(
            "risks",
            [],
        ) or []

        for risk in risks[:3]:
            reasons.append(
                f"Risk: {risk}"
            )

        if not reasons:
            reasons.append(
                "Signal based on available financial factors"
            )

        return reasons

    # =========================================================
    # Single Company Analysis
    # =========================================================

    def analyse_company(
        self,
        company_id,
        year="Mar 2024",
    ):
        """
        Generate the Day 21 decision signal for one company.
        """

        analysis = (
            self.company_engine
            .analyse_company(
                company_id,
                year,
            )
        )

        decision_score = (
            self.calculate_decision_score(
                analysis
            )
        )

        signal = self.classify_signal(
            decision_score
        )

        confidence = self.calculate_confidence(
            analysis
        )

        reasons = self.generate_reasons(
            analysis
        )

        return {
            "company_id":
                analysis["company_id"],

            "company_name":
                analysis["company_name"].strip(),

            "broad_sector":
                analysis["broad_sector"],

            "year":
                analysis["year"],

            "overall_rank":
                analysis["overall_rank"],

            "sector_rank":
                analysis["sector_rank"],

            "ranking_score":
                analysis["ranking_score"],

            "intelligence_score":
                analysis["intelligence_score"],

            "assessment":
                analysis["assessment"],

            "decision_score":
                decision_score,

            "signal":
                signal,

            "confidence":
                confidence,

            "strengths":
                analysis["strengths"],

            "risks":
                analysis["risks"],

            "reasons":
                reasons,

            "factor_scores":
                analysis["factor_scores"],
        }

    # =========================================================
    # Multiple Companies
    # =========================================================

    def analyse_companies(
        self,
        company_ids,
        year="Mar 2024",
        ignore_invalid=False,
    ):
        """Generate decision signals for multiple companies."""

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
                "At least one company is required."
            )

        rows = []
        invalid_companies = []

        for company_id in normalized:

            try:
                result = self.analyse_company(
                    company_id,
                    year,
                )

            except ValueError:
                if ignore_invalid:
                    invalid_companies.append(
                        company_id
                    )
                    continue

                raise

            rows.append(
                {
                    "company_id":
                        result["company_id"],

                    "company_name":
                        result["company_name"],

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
                        result[
                            "intelligence_score"
                        ],

                    "assessment":
                        result["assessment"],

                    "decision_score":
                        result["decision_score"],

                    "signal":
                        result["signal"],

                    "confidence":
                        result["confidence"],

                    "strength_count":
                        len(
                            result["strengths"]
                        ),

                    "risk_count":
                        len(
                            result["risks"]
                        ),

                    "reasons":
                        "; ".join(
                            result["reasons"]
                        ),
                }
            )

        if not rows:
            raise ValueError(
                "No valid companies available "
                "for decision analysis."
            )

        df = pd.DataFrame(rows)

        df["_signal_order"] = (
            df["signal"]
            .map(self.SIGNAL_ORDER)
            .fillna(0)
        )

        df = df.sort_values(
            by=[
                "decision_score",
                "_signal_order",
                "intelligence_score",
            ],
            ascending=[
                False,
                False,
                False,
            ],
            na_position="last",
        ).drop(
            columns=["_signal_order"]
        ).reset_index(
            drop=True
        )

        df.insert(
            0,
            "decision_rank",
            range(
                1,
                len(df) + 1,
            ),
        )

        df.attrs[
            "invalid_companies"
        ] = invalid_companies

        return df

    # =========================================================
    # Signal Distribution
    # =========================================================

    def signal_distribution(
        self,
        company_ids,
        year="Mar 2024",
    ):
        df = self.analyse_companies(
            company_ids,
            year,
        )

        result = (
            df["signal"]
            .value_counts()
            .rename_axis("signal")
            .reset_index(name="company_count")
        )

        result["weight_pct"] = (
            result["company_count"]
            / len(df)
            * 100
        ).round(2)

        return result

    # =========================================================
    # Export
    # =========================================================

    def export_csv(
        self,
        company_ids,
        year="Mar 2024",
        output_path=None,
    ):
        df = self.analyse_companies(
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
                / "decision_signals.csv"
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


def main():

    print("=" * 70)
    print("Sprint 3 - Day 21")
    print("N100 Decision Signal Engine")
    print("=" * 70)

    engine = DecisionSignalEngine()

    companies = [
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

    results = engine.analyse_companies(
        companies,
        year,
    )

    print(f"\nYear: {year}")
    print(
        f"Companies analysed: {len(results)}"
    )

    print(
        "\nDecision Signals"
    )

    print("-" * 70)

    columns = [
        "decision_rank",
        "company_id",
        "company_name",
        "decision_score",
        "signal",
        "confidence",
        "intelligence_score",
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
        "\nSignal Distribution"
    )

    print("-" * 70)

    print(
        engine.signal_distribution(
            companies,
            year,
        ).to_string(
            index=False
        )
    )

    print(
        "\nTCS Decision Analysis"
    )

    print("-" * 70)

    tcs = engine.analyse_company(
        "TCS",
        year,
    )

    print(
        f"Company          : "
        f"{tcs['company_name']}"
    )

    print(
        f"Decision Score   : "
        f"{tcs['decision_score']}"
    )

    print(
        f"Signal           : "
        f"{tcs['signal']}"
    )

    print(
        f"Confidence       : "
        f"{tcs['confidence']}"
    )

    print("\nReasons:")

    for reason in tcs["reasons"]:
        print(
            f"+ {reason}"
        )

    output_path = engine.export_csv(
        companies,
        year,
    )

    print(
        f"\nCSV generated:\n"
        f"{output_path}"
    )

    print(
        "\nDay 21 decision signal analysis "
        "completed successfully."
    )

    print(
        "\nNote: Decision signals are analytical "
        "model outputs, not investment advice."
    )


if __name__ == "__main__":
    main()