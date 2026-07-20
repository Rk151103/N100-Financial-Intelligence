"""
src/reports/company_report.py

Generate Company Financial Report
"""

import sqlite3
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


def generate_company_report():

    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        c.id,
        c.company_name,
        c.book_value,
        c.roe_percentage,
        c.roce_percentage,
        m.market_cap_crore,
        m.pe_ratio,
        m.pb_ratio
    FROM companies c
    LEFT JOIN market_cap m
    ON c.id = m.company_id
    """

    df = pd.read_sql(query, conn)

    output_file = OUTPUT_DIR / "company_report.csv"

    df.to_csv(output_file, index=False)

    print(df.head())

    print(f"\nReport saved to {output_file}")

    conn.close()


if __name__ == "__main__":
    generate_company_report()