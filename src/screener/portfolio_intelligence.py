"""
N100 Financial Intelligence Platform
Sprint 3 - Day 22
Portfolio Intelligence Engine

Provides portfolio-level analytics using the existing
Decision Signal Engine.

This module is for analytical purposes only and does not
constitute investment advice.
"""

from pathlib import Path

import pandas as pd

from src.screener.decision_engine import DecisionSignalEngine


BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "db" / "nifty100.db"
OUTPUT_DIR = BASE_DIR / "output"


class PortfolioIntelligenceEngine:
    """Analyse a portfolio of N100 companies."""

    def __init__(self, db_path=DB_PATH):
        self.db_path = Path(db_path)

        self.decision_engine = DecisionSignalEngine(
            db_path=self.db_path
        )

    # =========================================================
    # Portfolio Analysis
    # =========================================================

    def analyse_portfolio(
        self,
        company_ids,
        year="Mar 2024",
        ignore_invalid=False,
        weights=None,
    ):
        """Analyse companies with equal or custom portfolio weights."""
        df = self.decision_engine.analyse_companies(
            company_ids,
            year,
            ignore_invalid=ignore_invalid,
        ).copy()

        if df.empty:
            raise ValueError("Portfolio contains no valid companies.")

        if weights is None:
            df["portfolio_weight_pct"] = 100.0 / len(df)
        else:
            if not isinstance(weights, dict):
                raise TypeError("weights must be a dictionary of company_id - percentage.")

            normalized_weights = {
                str(company_id).strip().upper(): float(weight)
                for company_id, weight in weights.items()
            }

            if any(weight < 0 for weight in normalized_weights.values()):
                raise ValueError("Portfolio weights cannot be negative.")

            analysed_ids = (
                df["company_id"].astype(str).str.strip().str.upper().tolist()
            )

            missing_weights = [
                company_id
                for company_id in analysed_ids
                if company_id not in normalized_weights
            ]

            if missing_weights:
                raise ValueError(
                    "Missing portfolio weights for: " + ", ".join(missing_weights)
                )

            selected_weights = {
                company_id: normalized_weights[company_id]
                for company_id in analysed_ids
            }

            total_weight = sum(selected_weights.values())

            if abs(total_weight - 100.0) > 0.01:
                raise ValueError(
                    "Portfolio weights must total 100%%. "
                    f"Current total: {total_weight:.2f}%%."
                )

            df["portfolio_weight_pct"] = (
                df["company_id"]
                .astype(str)
                .str.strip()
                .str.upper()
                .map(selected_weights)
            )

        df["portfolio_weight_pct"] = pd.to_numeric(
            df["portfolio_weight_pct"], errors="coerce"
        ).round(2)

        return df

    # =========================================================
    # Sector Allocation
    # =========================================================

    def sector_allocation(
        self,
        company_ids,
        year="Mar 2024",
        ignore_invalid=False,
        weights=None,
    ):
        df = self.analyse_portfolio(
            company_ids,
            year,
            ignore_invalid,
            weights=weights,
        )

        result = (
            df.groupby(
                "broad_sector",
                dropna=False,
            )
            .agg(
                company_count=("company_id", "size"),
                weight_pct=("portfolio_weight_pct", "sum"),
            )
            .reset_index()
        )

        result["weight_pct"] = (
            pd.to_numeric(
                result["weight_pct"],
                errors="coerce",
            ).round(2)
        )

        return result.sort_values(
            ["weight_pct", "broad_sector"],
            ascending=[False, True],
        ).reset_index(drop=True)

    # =========================================================
    # Signal Distribution
    # =========================================================

    def signal_distribution(
        self,
        company_ids,
        year="Mar 2024",
        ignore_invalid=False,
        weights=None,
    ):
        df = self.analyse_portfolio(
            company_ids,
            year,
            ignore_invalid,
            weights=weights,
        )

        result = (
            df.groupby("signal", dropna=False)
            .agg(
                company_count=("company_id", "size"),
                weight_pct=("portfolio_weight_pct", "sum"),
            )
            .reset_index()
        )

        result["weight_pct"] = pd.to_numeric(
            result["weight_pct"], errors="coerce"
        ).round(2)

        return result.sort_values(
            ["weight_pct", "signal"],
            ascending=[False, True],
        ).reset_index(drop=True)

    # =========================================================
    # Assessment Distribution
    # =========================================================

    def assessment_distribution(
        self,
        company_ids,
        year="Mar 2024",
        ignore_invalid=False,
        weights=None,
    ):
        df = self.analyse_portfolio(
            company_ids,
            year,
            ignore_invalid,
            weights=weights,
        )

        result = (
            df.groupby("assessment", dropna=False)
            .agg(
                company_count=("company_id", "size"),
                weight_pct=("portfolio_weight_pct", "sum"),
            )
            .reset_index()
        )

        result["weight_pct"] = pd.to_numeric(
            result["weight_pct"], errors="coerce"
        ).round(2)

        return result.sort_values(
            ["weight_pct", "assessment"],
            ascending=[False, True],
        ).reset_index(drop=True)

    # =========================================================
    # Diversification
    # =========================================================

    def diversification_score(
        self,
        company_ids,
        year="Mar 2024",
        ignore_invalid=False,
        weights=None,
    ):
        """Calculate a 0-100 diversification score."""
        df = self.analyse_portfolio(
            company_ids,
            year,
            ignore_invalid,
            weights=weights,
        )

        sector_df = self.sector_allocation(
            company_ids,
            year,
            ignore_invalid,
            weights=weights,
        )

        company_count = len(df)
        sector_count = len(sector_df)

        if company_count == 0:
            return 0.0

        ideal_sector_count = min(company_count, 8)

        sector_diversity = min(
            sector_count / ideal_sector_count,
            1.0,
        ) * 100

        max_sector_weight = float(
            sector_df["weight_pct"].max()
        )

        concentration_score = max(
            0.0,
            100.0 - max_sector_weight,
        )

        score = (
            sector_diversity * 0.60
            + concentration_score * 0.40
        )

        return round(
            min(100.0, max(0.0, score)),
            2,
        )

    # =========================================================
    # Concentration Risk
    # =========================================================

    def concentration_risk(
        self,
        company_ids,
        year="Mar 2024",
        ignore_invalid=False,
        weights=None,
    ):
        sectors = self.sector_allocation(
            company_ids,
            year,
            ignore_invalid,
            weights=weights,
        )

        max_weight = float(
            sectors["weight_pct"].max()
        )

        if max_weight >= 60:
            return "High"

        if max_weight >= 40:
            return "Moderate"

        return "Low"

    # =========================================================
    # Portfolio Intelligence Score
    # =========================================================

    def portfolio_score(
        self,
        company_ids,
        year="Mar 2024",
        ignore_invalid=False,
        weights=None,
    ):
        """Calculate the weighted portfolio intelligence score."""
        df = self.analyse_portfolio(
            company_ids,
            year,
            ignore_invalid,
            weights=weights,
        )

        portfolio_weights = pd.to_numeric(
            df["portfolio_weight_pct"],
            errors="coerce",
        )

        intelligence_values = pd.to_numeric(
            df["intelligence_score"],
            errors="coerce",
        )

        decision_values = pd.to_numeric(
            df["decision_score"],
            errors="coerce",
        )

        intelligence_mask = (
            intelligence_values.notna()
            & portfolio_weights.notna()
        )

        decision_mask = (
            decision_values.notna()
            & portfolio_weights.notna()
        )

        if intelligence_mask.any():
            intelligence = (
                intelligence_values[intelligence_mask]
                * portfolio_weights[intelligence_mask]
            ).sum() / portfolio_weights[intelligence_mask].sum()
        else:
            intelligence = None

        if decision_mask.any():
            decision = (
                decision_values[decision_mask]
                * portfolio_weights[decision_mask]
            ).sum() / portfolio_weights[decision_mask].sum()
        else:
            decision = None

        diversification = self.diversification_score(
            company_ids,
            year,
            ignore_invalid,
            weights=weights,
        )

        values = [
            (intelligence, 0.40),
            (decision, 0.35),
            (diversification, 0.25),
        ]

        available = [
            (value, component_weight)
            for value, component_weight in values
            if value is not None and pd.notna(value)
        ]

        if not available:
            return None

        total_component_weight = sum(
            component_weight
            for _, component_weight in available
        )

        score = sum(
            value * component_weight
            for value, component_weight in available
        ) / total_component_weight

        return round(
            max(0.0, min(100.0, score)),
            2,
        )

    # =========================================================
    # Health Classification
    # =========================================================

    @staticmethod
    def classify_health(score):
        if score is None:
            return "Insufficient Data"

        if score >= 80:
            return "Strong"

        if score >= 65:
            return "Healthy"

        if score >= 50:
            return "Moderate"

        return "Weak"

    # =========================================================
    # Strongest / Weakest
    # =========================================================

    def strongest_holding(
        self,
        company_ids,
        year="Mar 2024",
        ignore_invalid=False,
    ):
        df = self.analyse_portfolio(
            company_ids,
            year,
            ignore_invalid,
        )

        return df.sort_values(
            "decision_score",
            ascending=False,
            na_position="last",
        ).iloc[0].to_dict()

    def weakest_holding(
        self,
        company_ids,
        year="Mar 2024",
        ignore_invalid=False,
    ):
        df = self.analyse_portfolio(
            company_ids,
            year,
            ignore_invalid,
        )

        valid = df[
            df["decision_score"].notna()
        ]

        if valid.empty:
            return df.iloc[-1].to_dict()

        return valid.sort_values(
            "decision_score",
            ascending=True,
        ).iloc[0].to_dict()

    # =========================================================
    # Summary
    # =========================================================

    def portfolio_summary(
        self,
        company_ids,
        year="Mar 2024",
        ignore_invalid=False,
        weights=None,
    ):
        df = self.analyse_portfolio(
            company_ids,
            year,
            ignore_invalid,
            weights=weights,
        )

        sectors = self.sector_allocation(
            company_ids,
            year,
            ignore_invalid,
            weights=weights,
        )

        strongest = self.strongest_holding(
            company_ids,
            year,
            ignore_invalid,
        )

        weakest = self.weakest_holding(
            company_ids,
            year,
            ignore_invalid,
        )

        score = self.portfolio_score(
            company_ids,
            year,
            ignore_invalid,
            weights=weights,
        )

        diversification = self.diversification_score(
            company_ids,
            year,
            ignore_invalid,
            weights=weights,
        )

        portfolio_weights = pd.to_numeric(
            df["portfolio_weight_pct"],
            errors="coerce",
        )

        intelligence_values = pd.to_numeric(
            df["intelligence_score"],
            errors="coerce",
        )

        decision_values = pd.to_numeric(
            df["decision_score"],
            errors="coerce",
        )

        intelligence_mask = (
            intelligence_values.notna()
            & portfolio_weights.notna()
        )

        decision_mask = (
            decision_values.notna()
            & portfolio_weights.notna()
        )

        average_intelligence = round(
            (
                intelligence_values[intelligence_mask]
                * portfolio_weights[intelligence_mask]
            ).sum()
            / portfolio_weights[intelligence_mask].sum(),
            2,
        )

        average_decision = round(
            (
                decision_values[decision_mask]
                * portfolio_weights[decision_mask]
            ).sum()
            / portfolio_weights[decision_mask].sum(),
            2,
        )

        return {
            "year": year,
            "company_count": len(df),
            "sector_count": len(sectors),
            "portfolio_score": score,
            "portfolio_health":
                self.classify_health(score),
            "average_intelligence_score":
                average_intelligence,
            "average_decision_score":
                average_decision,
            "diversification_score":
                diversification,
            "concentration_risk":
                self.concentration_risk(
                    company_ids,
                    year,
                    ignore_invalid,
                    weights=weights,
                ),
            "largest_sector":
                sectors.iloc[0]["broad_sector"],
            "largest_sector_weight_pct":
                float(sectors.iloc[0]["weight_pct"]),
            "strongest_company_id":
                strongest["company_id"],
            "strongest_company_name":
                strongest["company_name"],
            "strongest_decision_score":
                strongest["decision_score"],
            "weakest_company_id":
                weakest["company_id"],
            "weakest_company_name":
                weakest["company_name"],
            "weakest_decision_score":
                weakest["decision_score"],
            "invalid_companies":
                df.attrs.get("invalid_companies", []),
        }

    # =========================================================
    # Day 28 - Portfolio Rebalancing
    # =========================================================

    def suggest_rebalanced_weights(
        self,
        company_ids,
        current_weights=None,
        year="Mar 2024",
        ignore_invalid=False,
        step=10,
        max_weight=60.0,
    ):
        """
        Suggest a portfolio allocation using the existing
        portfolio intelligence scoring model.

        Candidate allocations are evaluated using portfolio_score,
        diversification and concentration risk. This is an
        analytical simulation and not investment advice.
        """
        company_ids = list(dict.fromkeys(company_ids))

        if not company_ids:
            raise ValueError(
                "At least one company is required."
            )

        if step <= 0 or step > 100:
            raise ValueError(
                "step must be greater than 0 and at most 100."
            )

        if max_weight <= 0 or max_weight > 100:
            raise ValueError(
                "max_weight must be greater than 0 and at most 100."
            )

        company_count = len(company_ids)

        minimum_required_cap = (
            100.0 / company_count
        )

        if max_weight + 1e-9 < minimum_required_cap:
            raise ValueError(
                "max_weight is too small for the number "
                "of portfolio companies."
            )

        # Validate companies and obtain the canonical portfolio.
        portfolio = self.analyse_portfolio(
            company_ids,
            year,
            ignore_invalid,
            weights=current_weights,
        )

        valid_company_ids = (
            portfolio["company_id"]
            .astype(str)
            .tolist()
        )

        company_count = len(valid_company_ids)

        if company_count == 1:
            only_company = valid_company_ids[0]

            proposed_weights = {
                only_company: 100.0,
            }

            proposed_summary = self.portfolio_summary(
                valid_company_ids,
                year,
                ignore_invalid,
                weights=proposed_weights,
            )

            current_summary = self.portfolio_summary(
                valid_company_ids,
                year,
                ignore_invalid,
                weights=current_weights,
            )

            return {
                "year": year,
                "company_count": 1,
                "current_weights": {
                    only_company: 100.0,
                },
                "recommended_weights":
                    proposed_weights,
                "current_portfolio_score":
                    current_summary[
                        "portfolio_score"
                    ],
                "recommended_portfolio_score":
                    proposed_summary[
                        "portfolio_score"
                    ],
                "portfolio_score_change": 0.0,
                "current_diversification_score":
                    current_summary[
                        "diversification_score"
                    ],
                "recommended_diversification_score":
                    proposed_summary[
                        "diversification_score"
                    ],
                "diversification_change": 0.0,
                "current_concentration_risk":
                    current_summary[
                        "concentration_risk"
                    ],
                "recommended_concentration_risk":
                    proposed_summary[
                        "concentration_risk"
                    ],
                "current_largest_sector_weight_pct":
                    current_summary[
                        "largest_sector_weight_pct"
                    ],
                "recommended_largest_sector_weight_pct":
                    proposed_summary[
                        "largest_sector_weight_pct"
                    ],
                "largest_sector_weight_change": 0.0,
                "recommended_summary":
                    proposed_summary,
            }

        # Current allocation is taken from analyse_portfolio so
        # equal-weight portfolios and custom portfolios use the
        # same normalized representation.
        current_weight_map = dict(
            zip(
                portfolio["company_id"],
                pd.to_numeric(
                    portfolio[
                        "portfolio_weight_pct"
                    ],
                    errors="coerce",
                ),
            )
        )

        current_weight_map = {
            str(company_id): round(
                float(weight),
                2,
            )
            for company_id, weight
            in current_weight_map.items()
        }

        current_summary = self.portfolio_summary(
            valid_company_ids,
            year,
            ignore_invalid,
            weights=current_weight_map,
        )

        best_weights = current_weight_map.copy()
        best_summary = current_summary
        best_score = current_summary[
            "portfolio_score"
        ]

        # Integer units make candidate totals exact and avoid
        # floating-point accumulation errors.
        units = round(100 / step)

        if abs(units * step - 100) > 1e-9:
            raise ValueError(
                "step must divide 100 exactly."
            )

        max_units = int(
            max_weight // step
        )

        def generate_allocations(
            remaining_units,
            positions_left,
            prefix,
        ):
            if positions_left == 1:
                if (
                    0 <= remaining_units
                    <= max_units
                ):
                    yield prefix + [
                        remaining_units
                    ]
                return

            upper = min(
                max_units,
                remaining_units,
            )

            for value in range(
                upper + 1
            ):
                yield from generate_allocations(
                    remaining_units - value,
                    positions_left - 1,
                    prefix + [value],
                )

        for allocation_units in generate_allocations(
            units,
            company_count,
            [],
        ):
            candidate_weights = {
                company_id: round(
                    allocation_unit * step,
                    2,
                )
                for company_id, allocation_unit
                in zip(
                    valid_company_ids,
                    allocation_units,
                )
            }

            candidate_summary = (
                self.portfolio_summary(
                    valid_company_ids,
                    year,
                    ignore_invalid,
                    weights=candidate_weights,
                )
            )

            candidate_score = (
                candidate_summary[
                    "portfolio_score"
                ]
            )

            if candidate_score is None:
                continue

            if (
                best_score is None
                or candidate_score > best_score
            ):
                best_score = candidate_score
                best_weights = candidate_weights
                best_summary = candidate_summary

            elif (
                candidate_score == best_score
                and candidate_summary[
                    "diversification_score"
                ]
                > best_summary[
                    "diversification_score"
                ]
            ):
                best_weights = candidate_weights
                best_summary = candidate_summary

        def difference(
            proposed_value,
            current_value,
        ):
            if (
                proposed_value is None
                or current_value is None
                or pd.isna(proposed_value)
                or pd.isna(current_value)
            ):
                return None

            return round(
                float(proposed_value)
                - float(current_value),
                2,
            )

        return {
            "year": year,
            "company_count": company_count,
            "current_weights":
                current_weight_map,
            "recommended_weights":
                best_weights,

            "current_portfolio_score":
                current_summary[
                    "portfolio_score"
                ],
            "recommended_portfolio_score":
                best_summary[
                    "portfolio_score"
                ],
            "portfolio_score_change":
                difference(
                    best_summary[
                        "portfolio_score"
                    ],
                    current_summary[
                        "portfolio_score"
                    ],
                ),

            "current_diversification_score":
                current_summary[
                    "diversification_score"
                ],
            "recommended_diversification_score":
                best_summary[
                    "diversification_score"
                ],
            "diversification_change":
                difference(
                    best_summary[
                        "diversification_score"
                    ],
                    current_summary[
                        "diversification_score"
                    ],
                ),

            "current_concentration_risk":
                current_summary[
                    "concentration_risk"
                ],
            "recommended_concentration_risk":
                best_summary[
                    "concentration_risk"
                ],

            "current_largest_sector_weight_pct":
                current_summary[
                    "largest_sector_weight_pct"
                ],
            "recommended_largest_sector_weight_pct":
                best_summary[
                    "largest_sector_weight_pct"
                ],
            "largest_sector_weight_change":
                difference(
                    best_summary[
                        "largest_sector_weight_pct"
                    ],
                    current_summary[
                        "largest_sector_weight_pct"
                    ],
                ),

            "recommended_summary":
                best_summary,
        }

    # =========================================================
    # Narrative
    # =========================================================

    def generate_summary(
        self,
        company_ids,
        year="Mar 2024",
        ignore_invalid=False,
        weights=None,
    ):
        summary = self.portfolio_summary(
            company_ids,
            year,
            ignore_invalid,
            weights=weights,
        )

        return (
            f"The portfolio contains "
            f"{summary['company_count']} companies "
            f"across {summary['sector_count']} sectors "
            f"for {summary['year']}. "
            f"Its portfolio intelligence score is "
            f"{summary['portfolio_score']}/100 and "
            f"is classified as "
            f"{summary['portfolio_health']}. "
            f"The diversification score is "
            f"{summary['diversification_score']}/100 "
            f"with {summary['concentration_risk'].lower()} "
            f"sector concentration risk. "
            f"{summary['strongest_company_name']} is the "
            f"strongest holding based on the analytical "
            f"decision score, while "
            f"{summary['weakest_company_name']} is the "
            f"weakest."
        )

    # =========================================================
    # Day 27 - Portfolio Scenario Analysis
    # =========================================================

    def compare_scenarios(
        self,
        company_ids,
        current_weights,
        proposed_weights,
        year="Mar 2024",
        ignore_invalid=False,
    ):
        """Compare current and proposed portfolio allocations."""

        current = self.portfolio_summary(
            company_ids,
            year,
            ignore_invalid,
            weights=current_weights,
        )

        proposed = self.portfolio_summary(
            company_ids,
            year,
            ignore_invalid,
            weights=proposed_weights,
        )

        def change(key):
            current_value = current.get(key)
            proposed_value = proposed.get(key)

            if (
                current_value is None
                or proposed_value is None
                or pd.isna(current_value)
                or pd.isna(proposed_value)
            ):
                return None

            return round(
                float(proposed_value)
                - float(current_value),
                2,
            )

        return {
            "year": year,
            "company_count": proposed["company_count"],

            "current_portfolio_score":
                current["portfolio_score"],
            "proposed_portfolio_score":
                proposed["portfolio_score"],
            "portfolio_score_change":
                change("portfolio_score"),

            "current_portfolio_health":
                current["portfolio_health"],
            "proposed_portfolio_health":
                proposed["portfolio_health"],

            "current_diversification_score":
                current["diversification_score"],
            "proposed_diversification_score":
                proposed["diversification_score"],
            "diversification_change":
                change("diversification_score"),

            "current_average_intelligence_score":
                current["average_intelligence_score"],
            "proposed_average_intelligence_score":
                proposed["average_intelligence_score"],
            "average_intelligence_change":
                change("average_intelligence_score"),

            "current_average_decision_score":
                current["average_decision_score"],
            "proposed_average_decision_score":
                proposed["average_decision_score"],
            "average_decision_change":
                change("average_decision_score"),

            "current_concentration_risk":
                current["concentration_risk"],
            "proposed_concentration_risk":
                proposed["concentration_risk"],

            "current_largest_sector":
                current["largest_sector"],
            "proposed_largest_sector":
                proposed["largest_sector"],

            "current_largest_sector_weight_pct":
                current["largest_sector_weight_pct"],
            "proposed_largest_sector_weight_pct":
                proposed["largest_sector_weight_pct"],
            "largest_sector_weight_change":
                change("largest_sector_weight_pct"),

            "current_summary": current,
            "proposed_summary": proposed,
        }

    # =========================================================
    # Day 29 - Portfolio Rebalancing Plan
    # =========================================================

    def generate_rebalancing_plan(
        self,
        company_ids,
        current_weights=None,
        year="Mar 2024",
        ignore_invalid=False,
        step=5,
        max_weight=40,
    ):
        """Generate holding-level actions for portfolio rebalancing."""

        result = self.suggest_rebalanced_weights(
            company_ids,
            current_weights=current_weights,
            year=year,
            ignore_invalid=ignore_invalid,
            step=step,
            max_weight=max_weight,
        )

        current = result["current_weights"]
        recommended = result["recommended_weights"]

        portfolio = self.analyse_portfolio(
            company_ids,
            year,
            ignore_invalid,
            weights=current,
        )

        company_names = dict(
            zip(
                portfolio["company_id"],
                portfolio["company_name"],
            )
        )

        rows = []

        for company_id in current:
            current_weight = float(
                current.get(company_id, 0.0)
            )

            recommended_weight = float(
                recommended.get(company_id, 0.0)
            )

            weight_change = round(
                recommended_weight - current_weight,
                2,
            )

            if weight_change > 0:
                action = "Increase"
            elif weight_change < 0:
                action = "Reduce"
            else:
                action = "Maintain"

            rows.append(
                {
                    "company_id": company_id,
                    "company_name": company_names.get(
                        company_id,
                        company_id,
                    ),
                    "current_weight_pct": round(
                        current_weight,
                        2,
                    ),
                    "recommended_weight_pct": round(
                        recommended_weight,
                        2,
                    ),
                    "weight_change_pct": weight_change,
                    "action": action,
                }
            )

        plan = pd.DataFrame(rows)

        if not plan.empty:
            action_order = {
                "Reduce": 1,
                "Increase": 2,
                "Maintain": 3,
            }

            plan["_action_order"] = (
                plan["action"]
                .map(action_order)
                .fillna(4)
            )

            plan["_change_size"] = (
                plan["weight_change_pct"]
                .abs()
            )

            plan = (
                plan.sort_values(
                    by=[
                        "_action_order",
                        "_change_size",
                        "company_name",
                    ],
                    ascending=[
                        True,
                        False,
                        True,
                    ],
                )
                .drop(
                    columns=[
                        "_action_order",
                        "_change_size",
                    ]
                )
                .reset_index(drop=True)
            )

        plan.attrs["rebalancing_result"] = result

        return plan

    # =========================================================
    # Day 31 - Portfolio Rebalancing Action Summary
    # =========================================================

    def rebalancing_summary(
        self,
        company_ids,
        current_weights=None,
        year="Mar 2024",
        ignore_invalid=False,
        step=5,
        max_weight=40,
    ):
        """Summarise holding-level portfolio rebalancing actions."""

        plan = self.generate_rebalancing_plan(
            company_ids,
            current_weights=current_weights,
            year=year,
            ignore_invalid=ignore_invalid,
            step=step,
            max_weight=max_weight,
        )

        result = plan.attrs.get(
            "rebalancing_result",
            {},
        )

        if plan.empty:
            return {
                "year": year,
                "holding_count": 0,
                "increase_count": 0,
                "reduce_count": 0,
                "maintain_count": 0,
                "changed_holdings_count": 0,
                "total_increase_pct": 0.0,
                "total_reduction_pct": 0.0,
                "portfolio_turnover_pct": 0.0,
                "largest_increase_company_id": None,
                "largest_increase_company_name": None,
                "largest_increase_pct": 0.0,
                "largest_reduction_company_id": None,
                "largest_reduction_company_name": None,
                "largest_reduction_pct": 0.0,
                "summary": "No portfolio holdings were available.",
                "rebalancing_result": result,
            }

        increase_mask = (
            plan["action"] == "Increase"
        )

        reduce_mask = (
            plan["action"] == "Reduce"
        )

        maintain_mask = (
            plan["action"] == "Maintain"
        )

        increase_count = int(
            increase_mask.sum()
        )

        reduce_count = int(
            reduce_mask.sum()
        )

        maintain_count = int(
            maintain_mask.sum()
        )

        changed_holdings_count = (
            increase_count + reduce_count
        )

        total_increase = round(
            float(
                plan.loc[
                    increase_mask,
                    "weight_change_pct",
                ].sum()
            ),
            2,
        )

        total_reduction = round(
            abs(
                float(
                    plan.loc[
                        reduce_mask,
                        "weight_change_pct",
                    ].sum()
                )
            ),
            2,
        )

        portfolio_turnover = round(
            (
                total_increase
                + total_reduction
            )
            / 2.0,
            2,
        )

        largest_increase_company_id = None
        largest_increase_company_name = None
        largest_increase_pct = 0.0

        if increase_mask.any():
            increase_rows = plan.loc[
                increase_mask
            ]

            largest_increase_index = (
                increase_rows[
                    "weight_change_pct"
                ].idxmax()
            )

            largest_increase_row = plan.loc[
                largest_increase_index
            ]

            largest_increase_company_id = (
                largest_increase_row[
                    "company_id"
                ]
            )

            largest_increase_company_name = (
                largest_increase_row[
                    "company_name"
                ]
            )

            largest_increase_pct = round(
                float(
                    largest_increase_row[
                        "weight_change_pct"
                    ]
                ),
                2,
            )

        largest_reduction_company_id = None
        largest_reduction_company_name = None
        largest_reduction_pct = 0.0

        if reduce_mask.any():
            reduce_rows = plan.loc[
                reduce_mask
            ]

            largest_reduction_index = (
                reduce_rows[
                    "weight_change_pct"
                ].idxmin()
            )

            largest_reduction_row = plan.loc[
                largest_reduction_index
            ]

            largest_reduction_company_id = (
                largest_reduction_row[
                    "company_id"
                ]
            )

            largest_reduction_company_name = (
                largest_reduction_row[
                    "company_name"
                ]
            )

            largest_reduction_pct = round(
                abs(
                    float(
                        largest_reduction_row[
                            "weight_change_pct"
                        ]
                    )
                ),
                2,
            )

        summary_parts = [
            (
                f"The rebalancing plan contains "
                f"{len(plan)} holdings."
            ),
            (
                f"{increase_count} "
                f"{'holding is' if increase_count == 1 else 'holdings are'} "
                f"marked for increase, {reduce_count} for reduction, "
                f"and {maintain_count} for maintenance."
            ),
            (
                f"Total proposed weight increase is "
                f"{total_increase:.2f}% and total proposed "
                f"weight reduction is "
                f"{total_reduction:.2f}%."
            ),
            (
                f"Estimated portfolio turnover is "
                f"{portfolio_turnover:.2f}%."
            ),
        ]

        if largest_increase_company_name:
            summary_parts.append(
                f"The largest increase is "
                f"{largest_increase_company_name} "
                f"at +{largest_increase_pct:.2f}%."
            )

        if largest_reduction_company_name:
            summary_parts.append(
                f"The largest reduction is "
                f"{largest_reduction_company_name} "
                f"at -{largest_reduction_pct:.2f}%."
            )

        return {
            "year": year,
            "holding_count": len(plan),
            "increase_count": increase_count,
            "reduce_count": reduce_count,
            "maintain_count": maintain_count,
            "changed_holdings_count": changed_holdings_count,
            "total_increase_pct": total_increase,
            "total_reduction_pct": total_reduction,
            "portfolio_turnover_pct": portfolio_turnover,
            "largest_increase_company_id":
                largest_increase_company_id,
            "largest_increase_company_name":
                largest_increase_company_name,
            "largest_increase_pct":
                largest_increase_pct,
            "largest_reduction_company_id":
                largest_reduction_company_id,
            "largest_reduction_company_name":
                largest_reduction_company_name,
            "largest_reduction_pct":
                largest_reduction_pct,
            "summary": " ".join(summary_parts),
            "rebalancing_result": result,
        }

    # =========================================================
    # Day 30 - Portfolio Rebalancing Report Export
    # =========================================================

    def export_rebalancing_report(
        self,
        company_ids,
        current_weights=None,
        year="Mar 2024",
        output_path=None,
        ignore_invalid=False,
        step=5,
        max_weight=40,
    ):
        """Generate and export the portfolio rebalancing plan."""

        plan = self.generate_rebalancing_plan(
            company_ids,
            current_weights=current_weights,
            year=year,
            ignore_invalid=ignore_invalid,
            step=step,
            max_weight=max_weight,
        )

        result = plan.attrs.get(
            "rebalancing_result",
            {},
        )

        if output_path is None:
            OUTPUT_DIR.mkdir(
                parents=True,
                exist_ok=True,
            )

            output_path = (
                OUTPUT_DIR
                / "portfolio_rebalancing_report.csv"
            )
        else:
            output_path = Path(output_path)

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

        export_df = plan.copy()

        export_df.to_csv(
            output_path,
            index=False,
        )

        return {
            "output_path": output_path,
            "row_count": len(export_df),
            "year": year,
            "current_portfolio_score": result.get(
                "current_portfolio_score"
            ),
            "recommended_portfolio_score": result.get(
                "recommended_portfolio_score"
            ),
            "portfolio_score_change": result.get(
                "portfolio_score_change"
            ),
            "current_diversification_score": result.get(
                "current_diversification_score"
            ),
            "recommended_diversification_score": result.get(
                "recommended_diversification_score"
            ),
            "diversification_change": result.get(
                "diversification_change"
            ),
            "current_concentration_risk": result.get(
                "current_concentration_risk"
            ),
            "recommended_concentration_risk": result.get(
                "recommended_concentration_risk"
            ),
            "current_largest_sector_weight_pct": result.get(
                "current_largest_sector_weight_pct"
            ),
            "recommended_largest_sector_weight_pct": result.get(
                "recommended_largest_sector_weight_pct"
            ),
            "largest_sector_weight_change": result.get(
                "largest_sector_weight_change"
            ),
        }

    # =========================================================
    # CSV Export
    # =========================================================

    def export_csv(
        self,
        company_ids,
        year="Mar 2024",
        output_path=None,
        ignore_invalid=False,
        weights=None,
    ):
        df = self.analyse_portfolio(
            company_ids,
            year,
            ignore_invalid,
            weights=weights,
        )

        if output_path is None:
            OUTPUT_DIR.mkdir(
                parents=True,
                exist_ok=True,
            )

            output_path = (
                OUTPUT_DIR
                / "portfolio_intelligence.csv"
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

        return output_path


def main():
    print("=" * 72)
    print("Sprint 3 - Day 22")
    print("N100 Portfolio Intelligence Engine")
    print("=" * 72)

    engine = PortfolioIntelligenceEngine()

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

    results = engine.analyse_portfolio(
        portfolio,
        year,
    )

    print(f"\nYear: {year}")
    print(
        f"Companies analysed: {len(results)}"
    )

    print("\nPortfolio Holdings")
    print("-" * 72)

    columns = [
        "company_id",
        "company_name",
        "broad_sector",
        "decision_score",
        "signal",
        "intelligence_score",
        "portfolio_weight_pct",
    ]

    print(
        results[columns].to_string(
            index=False
        )
    )

    print("\nSector Allocation")
    print("-" * 72)

    print(
        engine.sector_allocation(
            portfolio,
            year,
        ).to_string(
            index=False
        )
    )

    print("\nSignal Distribution")
    print("-" * 72)

    print(
        engine.signal_distribution(
            portfolio,
            year,
        ).to_string(
            index=False
        )
    )

    print("\nPortfolio Summary")
    print("-" * 72)

    summary = engine.portfolio_summary(
        portfolio,
        year,
    )

    for key, value in summary.items():
        print(
            f"{key:32}: {value}"
        )

    print("\nNarrative")
    print("-" * 72)

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

    print(
        f"\nCSV generated:\n{output_path}"
    )

    print(
        "\nDay 22 portfolio intelligence "
        "analysis completed successfully."
    )

    print(
        "\nNote: Portfolio intelligence outputs "
        "are analytical model signals, not "
        "investment advice."
    )


if __name__ == "__main__":
    main()