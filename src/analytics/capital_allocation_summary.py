"""
Sprint 5 - Day 32
Capital Allocation Summary
"""

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "output"


class CapitalAllocationSummary:

    def __init__(self):
        self.df = pd.read_csv(
            OUTPUT_DIR / "capital_allocation.csv"
        )

    def pattern_summary(self):

        summary = (
            self.df["pattern_label"]
            .value_counts()
            .reset_index()
        )

        summary.columns = [
            "pattern_label",
            "company_count",
        ]

        summary.to_csv(
            OUTPUT_DIR /
            "capital_allocation_summary.csv",
            index=False,
        )

        print("\nPattern Distribution")
        print(summary)

    def pattern_changes(self):

        changes = []

        for company, group in self.df.groupby("company_id"):

            patterns = (
                group.sort_values("year")
                ["pattern_label"]
                .tolist()
            )

            unique_patterns = list(dict.fromkeys(patterns))

            if len(unique_patterns) > 1:

                changes.append(
                    {
                        "company_id": company,
                        "pattern_changes":
                            " -> ".join(unique_patterns),
                    }
                )

        change_df = pd.DataFrame(changes)

        change_df.to_csv(
            OUTPUT_DIR /
            "pattern_changes.csv",
            index=False,
        )

        print(
            f"\nCompanies with pattern changes: "
            f"{len(change_df)}"
        )

    def run(self):

        self.pattern_summary()

        self.pattern_changes()

        print(
            "\nCapital Allocation Summary completed."
        )


if __name__ == "__main__":
    CapitalAllocationSummary().run()