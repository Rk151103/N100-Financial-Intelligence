"""
src/etl/database_loader.py

Sprint 1 - Day 05
Generic Database Loader
"""

from pathlib import Path
import sqlite3
import traceback
import pandas as pd

from src.etl.config import TABLES

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"


class DatabaseLoader:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.execute("PRAGMA foreign_keys = ON")

    def load_table(self, config):

        table = config["table"]
        file = config["file"]
        header = config["header"]
        drop = config["drop"]

        print("\n" + "=" * 60)
        print(f"Loading {table}")
        print("=" * 60)

        if not file.exists():
            print(f"❌ File not found: {file}")
            return

        df = pd.read_excel(file, header=header)

        if drop:
            df.drop(columns=drop, inplace=True, errors="ignore")

        print(f"Rows    : {len(df)}")
        print(f"Columns : {len(df.columns)}")

        # ----------------------------
        # Special validation
        # ----------------------------
        if table == "analysis":

            companies = pd.read_sql(
                "SELECT id FROM companies",
                self.conn
            )

            valid_ids = set(companies["id"])

            invalid = df[
                ~df["company_id"].isin(valid_ids)
            ]

            if not invalid.empty:
                print("\n⚠ Invalid company IDs found:")
                print(invalid["company_id"].drop_duplicates())

            df = df[
                df["company_id"].isin(valid_ids)
            ]

            print(f"\nValid rows: {len(df)}")

        # ----------------------------
        # Delete existing rows
        # ----------------------------
        try:
            self.conn.execute(f"DELETE FROM {table}")
            self.conn.commit()
        except Exception:
            pass

        # ----------------------------
        # Insert into SQLite
        # ----------------------------
        try:

            df.to_sql(
                table,
                self.conn,
                if_exists="append",
                index=False
            )

            total = pd.read_sql(
                f"SELECT COUNT(*) AS total FROM {table}",
                self.conn
            )

            print(total)

            print(f"✅ {table} loaded successfully")

        except Exception:

            print(f"\n❌ Failed to load table: {table}\n")

            traceback.print_exc()

    def run(self):

        for table in TABLES:
            self.load_table(table)

        print("\n" + "=" * 60)
        print("Sprint 1 Day 05 Finished")
        print("=" * 60)

    def close(self):
        self.conn.close()


def main():

    loader = DatabaseLoader()

    loader.run()

    loader.close()


if __name__ == "__main__":
    main()