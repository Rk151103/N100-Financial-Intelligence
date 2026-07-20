"""
src/reports/sector_report.py
"""

import sqlite3
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


def generate_sector_report():

    conn = sqlite3.connect(DB_PATH)

    companies = pd.read_sql("SELECT * FROM companies", conn)

    report = companies[
        [
            "company_name",
            "roe_percentage",
            "roce_percentage",
        ]
    ]

    report.to_csv(
        OUTPUT_DIR / "sector_report.csv",
        index=False
    )

    print(report.head())

    conn.close()


if __name__ == "__main__":
    generate_sector_report()