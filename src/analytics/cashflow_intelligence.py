"""
Sprint 5 - Day 31
Cash Flow Intelligence
"""

from pathlib import Path

import pandas as pd

from src.reports.company_report import CompanyReportGenerator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


class CashFlowIntelligence:

    def __init__(self):
        self.df = CompanyReportGenerator().generate()

    def cfo_quality(self, cfo):

        if pd.isna(cfo):
            return None

        if cfo > 0:
            return "High Quality"

        if cfo == 0:
            return "Moderate"

        return "Accrual Risk"

    def capex_label(self, capex):

        if pd.isna(capex):
            return None

        if capex < 100:
            return "Asset Light"

        if capex < 500:
            return "Moderate"

        return "Capital Intensive"

    def run(self):

        result = self.df.copy()

        result["cfo_quality_label"] = (
            result["cash_from_operations_cr"]
            .apply(self.cfo_quality)
        )

        result["capex_label"] = (
            result["capex_cr"]
            .apply(self.capex_label)
        )

        result["distress_flag"] = (
            (result["cash_from_operations_cr"] < 0)
            &
            (result["free_cash_flow_cr"] < 0)
        )

        result["deleveraging_flag"] = (
            result["total_debt_cr"] == 0
        )

        result.to_excel(
            OUTPUT_DIR /
            "cashflow_intelligence.xlsx",
            index=False,
        )

        result[
            result["distress_flag"]
        ].to_csv(
            OUTPUT_DIR /
            "distress_alerts.csv",
            index=False,
        )

        print(result.head())

        print(
            "\nCash Flow Intelligence generated."
        )


if __name__ == "__main__":
    CashFlowIntelligence().run()