"""
Sprint 5 - Day 29
NLP Analysis Parser
"""

import re
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = PROJECT_ROOT / "data" / "raw" / "core" / "analysis.xlsx"

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

PATTERN = re.compile(r"(\d+)\s*Years?:?\s*([\d.]+)%")


def parse_text(text):

    if pd.isna(text):
        return None

    match = PATTERN.search(str(text))

    if match:
        return {
            "period_years": int(match.group(1)),
            "value_pct": float(match.group(2)),
        }

    return None


def main():

    df = pd.read_excel(DATA_PATH, header=1)

    parsed = []
    failures = []

    target_columns = [
        "compounded_sales_growth",
        "compounded_profit_growth",
        "stock_price_cagr",
        "roe",
    ]

    for _, row in df.iterrows():

        company = row["company_id"]

        for column in target_columns:

            result = parse_text(row.get(column))

            if result:

                parsed.append(
                    {
                        "company_id": company,
                        "metric_type": column,
                        **result,
                    }
                )

            else:

                failures.append(
                    {
                        "company_id": company,
                        "metric_type": column,
                        "text": row.get(column),
                    }
                )

    pd.DataFrame(parsed).to_csv(
        OUTPUT_DIR / "analysis_parsed.csv",
        index=False,
    )

    pd.DataFrame(failures).to_csv(
        OUTPUT_DIR / "parse_failures.csv",
        index=False,
    )

    print("Parsing completed.")
    print(f"Parsed : {len(parsed)}")
    print(f"Failed : {len(failures)}")


if __name__ == "__main__":
    main()
