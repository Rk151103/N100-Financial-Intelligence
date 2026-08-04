"""
Sprint 5 – Day 30
Auto Pros & Cons Generator
"""

from pathlib import Path

import pandas as pd

from src.reports.company_report import CompanyReportGenerator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


class ProsConsGenerator:

    def __init__(self):
        self.df = CompanyReportGenerator().generate()

    def confidence(self, score):
        return min(100, max(60, int(score)))

    def generate(self):

        results = []

        for _, row in self.df.iterrows():

            company = row["company_id"]

            # ---------- PRO RULES ----------

            if row["return_on_equity_pct"] >= 20:

                results.append({
                    "company_id": company,
                    "type": "pro",
                    "rule_id": "P1",
                    "text": "Consistently high return on equity above 20% demonstrates exceptional capital efficiency.",
                    "confidence_pct": self.confidence(90)
                })

            if row["free_cash_flow_cr"] > 0:

                results.append({
                    "company_id": company,
                    "type": "pro",
                    "rule_id": "P2",
                    "text": "Positive free cash flow indicates healthy business fundamentals.",
                    "confidence_pct": self.confidence(85)
                })

            if row["debt_to_equity"] == 0:

                results.append({
                    "company_id": company,
                    "type": "pro",
                    "rule_id": "P3",
                    "text": "Debt-free balance sheet provides financial flexibility.",
                    "confidence_pct": self.confidence(95)
                })

            # ---------- CON RULES ----------

            if row["debt_to_equity"] > 2:

                results.append({
                    "company_id": company,
                    "type": "con",
                    "rule_id": "C1",
                    "text": f"Debt-to-equity ratio of {row['debt_to_equity']:.2f} is elevated.",
                    "confidence_pct": self.confidence(90)
                })

            if row["free_cash_flow_cr"] < 0:

                results.append({
                    "company_id": company,
                    "type": "con",
                    "rule_id": "C2",
                    "text": "Negative free cash flow raises concern about cash generation.",
                    "confidence_pct": self.confidence(80)
                })

            if row["operating_profit_margin_pct"] < 10:

                results.append({
                    "company_id": company,
                    "type": "con",
                    "rule_id": "C3",
                    "text": "Operating margin below 10% suggests profitability pressure.",
                    "confidence_pct": self.confidence(75)
                })

        result = pd.DataFrame(results)

        output_file = OUTPUT_DIR / "pros_cons_generated.csv"

        result.to_csv(
            output_file,
            index=False,
        )

        print(result.head())

        print(f"\nGenerated {len(result)} Pros/Cons")

        print(f"\nSaved : {output_file}")


if __name__ == "__main__":
    ProsConsGenerator().generate()