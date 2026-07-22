"""
src/screener/presets.py

N100 Financial Intelligence Platform
Sprint 3 - Day 16
Advanced Screener Presets
"""

from src.screener.engine import ScreenerEngine


class ScreenerPresets:
    """
    Reusable screening strategies built on top of ScreenerEngine.
    """

    PRESETS = {
        "high_quality": {
            "roe_min": 15,
            "debt_to_equity_max": 1,
            "opm_min": 10,
        },

        "high_growth": {
            "revenue_cagr_5yr_min": 10,
            "pat_cagr_5yr_min": 10,
            "eps_cagr_5yr_min": 10,
        },

        "low_debt": {
            "debt_to_equity_max": 0.5,
        },

        "strong_cash_flow": {
            "fcf_min": 0,
            "icr_min": 3,
        },

        "efficient_business": {
            "roe_min": 15,
            "asset_turnover_min": 1,
        },

        "growth_quality": {
            "roe_min": 15,
            "debt_to_equity_max": 1,
            "revenue_cagr_5yr_min": 10,
            "pat_cagr_5yr_min": 10,
        },

        "conservative_quality": {
            "roe_min": 15,
            "debt_to_equity_max": 0.5,
            "icr_min": 5,
            "fcf_min": 0,
        },
    }

    def __init__(self, engine=None):
        self.engine = engine or ScreenerEngine()

    @classmethod
    def available_presets(cls):
        """Return all available preset names."""

        return list(cls.PRESETS.keys())

    @classmethod
    def get_preset(cls, preset_name):
        """Return filters for a preset."""

        if preset_name not in cls.PRESETS:
            raise ValueError(
                f"Unknown preset: {preset_name}. "
                f"Available presets: {', '.join(cls.available_presets())}"
            )

        return cls.PRESETS[preset_name].copy()

    def run(self, preset_name, year=None):
        """Run one preset through the screener engine."""

        filters = self.get_preset(preset_name)

        return self.engine.screen(
            filters=filters,
            year=year,
        )

    def run_all(self, year=None):
        """Run all presets and return results in a dictionary."""

        results = {}

        for preset_name in self.available_presets():
            results[preset_name] = self.run(
                preset_name,
                year=year,
            )

        return results

    def summary(self, year=None):
        """Return the number of matching companies for each preset."""

        results = self.run_all(year=year)

        return {
            preset_name: len(df)
            for preset_name, df in results.items()
        }


def main():
    print("=" * 55)
    print("Sprint 3 - Day 16")
    print("N100 Advanced Screener Presets")
    print("=" * 55)

    presets = ScreenerPresets()

    year = "Mar 2024"

    print(f"\nScreening year: {year}")

    print("\nAvailable presets:")

    for preset_name in presets.available_presets():
        print(f"- {preset_name}")

    print("\nPreset Results")
    print("-" * 55)

    summary = presets.summary(year=year)

    for preset_name, count in summary.items():
        print(
            f"{preset_name:<25} "
            f"{count:>5} companies"
        )

    print("\nTop High Quality Companies")
    print("-" * 55)

    high_quality = presets.run(
        "high_quality",
        year=year,
    )

    display_columns = [
        "company_id",
        "company_name",
        "broad_sector",
        "return_on_equity_pct",
        "debt_to_equity",
        "operating_profit_margin_pct",
        "composite_quality_score",
    ]

    available_columns = [
        column
        for column in display_columns
        if column in high_quality.columns
    ]

    if high_quality.empty:
        print("No companies matched.")
    else:
        print(
            high_quality[
                available_columns
            ]
            .head(10)
            .to_string(index=False)
        )

    print("\nDay 16 advanced screener presets completed successfully.")


if __name__ == "__main__":
    main()