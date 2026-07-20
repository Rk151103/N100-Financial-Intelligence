"""
src/etl/database_loader.py

Sprint 1 - Day 05
Robust Generic Database Loader
"""

from pathlib import Path
import sqlite3
import traceback
import pandas as pd

from src.etl.config import TABLES


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
OUTPUT_PATH = PROJECT_ROOT / "output"

OUTPUT_PATH.mkdir(parents=True, exist_ok=True)


class DatabaseLoader:

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.execute("PRAGMA foreign_keys = ON")

        self.rejected_rows = []
        self.audit_rows = []

    # -------------------------------------------------
    # Get valid company IDs
    # -------------------------------------------------

    def get_valid_company_ids(self):

        companies = pd.read_sql(
            "SELECT id FROM companies",
            self.conn
        )

        return set(
            companies["id"]
            .astype(str)
            .str.strip()
        )

    # -------------------------------------------------
    # Validate Foreign Keys
    # -------------------------------------------------

    def validate_company_ids(self, df, table):

        if "company_id" not in df.columns:
            return df

        valid_ids = self.get_valid_company_ids()

        df["company_id"] = (
            df["company_id"]
            .astype(str)
            .str.strip()
        )

        invalid_mask = ~df["company_id"].isin(valid_ids)

        invalid = df[invalid_mask].copy()

        if not invalid.empty:

            print("\n⚠ Invalid company IDs:")

            print(
                invalid["company_id"]
                .drop_duplicates()
                .tolist()
            )

            invalid["source_table"] = table
            invalid["rejection_reason"] = "Invalid company_id"

            self.rejected_rows.append(invalid)

        return df[~invalid_mask].copy()

    # -------------------------------------------------
    # Remove Duplicate Primary Keys
    # -------------------------------------------------

    def remove_duplicates(self, df, table):

        primary_keys = {

            "documents": [
                "company_id",
                "year"
            ],

            "profitandloss": [
                "company_id",
                "year"
            ],

            "balancesheet": [
                "company_id",
                "year"
            ],

            "cashflow": [
                "company_id",
                "year"
            ],

            "stock_prices": [
                "company_id",
                "date"
            ],

            "market_cap": [
                "company_id",
                "year"
            ],

            "financial_ratios": [
                "company_id",
                "year"
            ],

            "sectors": [
                "company_id"
            ],

            "peer_groups": [
                "peer_group_name",
                "company_id"
            ]
        }

        keys = primary_keys.get(table)

        if not keys:
            return df

        if not all(
            key in df.columns
            for key in keys
        ):
            return df

        duplicate_mask = df.duplicated(
            subset=keys,
            keep="first"
        )

        duplicates = df[
            duplicate_mask
        ].copy()

        if not duplicates.empty:

            print(
                f"⚠ Removing {len(duplicates)} "
                f"duplicate rows from {table}"
            )

            duplicates["source_table"] = table

            duplicates[
                "rejection_reason"
            ] = "Duplicate primary key"

            self.rejected_rows.append(
                duplicates
            )

        return df[
            ~duplicate_mask
        ].copy()

    # -------------------------------------------------
    # Load Individual Table
    # -------------------------------------------------

    def load_table(self, config):

        table = config["table"]
        file_path = config["file"]
        header = config["header"]
        drop = config["drop"]

        print("\n" + "=" * 60)
        print(f"Loading {table}")
        print("=" * 60)

        if not file_path.exists():

            print(
                f"❌ File not found: "
                f"{file_path}"
            )

            self.audit_rows.append({
                "table": table,
                "source_rows": 0,
                "loaded_rows": 0,
                "status": "FILE NOT FOUND"
            })

            return

        try:

            # -----------------------------------------
            # Read Excel
            # -----------------------------------------

            df = pd.read_excel(
                file_path,
                header=header
            )

            # -----------------------------------------
            # Normalize column names
            #
            # Example:
            # Year -> year
            # Annual_Report -> annual_report
            # -----------------------------------------

            df.columns = (
                df.columns
                .astype(str)
                .str.strip()
                .str.lower()
            )

            source_rows = len(df)

            # -----------------------------------------
            # Drop unwanted columns
            # -----------------------------------------

            if drop:

                # Normalize configured drop names too
                drop = [
                    str(column)
                    .strip()
                    .lower()
                    for column in drop
                ]

                df.drop(
                    columns=drop,
                    inplace=True,
                    errors="ignore"
                )

            print(
                f"Source rows : "
                f"{source_rows}"
            )

            print(
                f"Columns     : "
                f"{len(df.columns)}"
            )

            print(
                f"Column names: "
                f"{df.columns.tolist()}"
            )

            # -----------------------------------------
            # Normalize company_id
            # -----------------------------------------

            if "company_id" in df.columns:

                df["company_id"] = (
                    df["company_id"]
                    .astype(str)
                    .str.strip()
                )

            # -----------------------------------------
            # Validate company foreign keys
            # -----------------------------------------

            if table != "companies":

                df = self.validate_company_ids(
                    df,
                    table
                )

            # -----------------------------------------
            # Remove duplicate primary keys
            # -----------------------------------------

            df = self.remove_duplicates(
                df,
                table
            )

            print(
                f"Valid rows  : "
                f"{len(df)}"
            )

            # -----------------------------------------
            # Clear existing data
            # -----------------------------------------

            self.conn.execute(
                f"DELETE FROM {table}"
            )

            self.conn.commit()

            # -----------------------------------------
            # Insert into database
            # -----------------------------------------

            df.to_sql(
                table,
                self.conn,
                if_exists="append",
                index=False
            )

            self.conn.commit()

            # -----------------------------------------
            # Verify row count
            # -----------------------------------------

            total = self.conn.execute(
                f"SELECT COUNT(*) "
                f"FROM {table}"
            ).fetchone()[0]

            print(
                f"✅ {table} loaded successfully: "
                f"{total} rows"
            )

            # -----------------------------------------
            # Add audit record
            # -----------------------------------------

            self.audit_rows.append({
                "table": table,
                "source_rows": source_rows,
                "loaded_rows": total,
                "status": "SUCCESS"
            })

        except Exception as error:

            self.conn.rollback()

            print(
                f"\n❌ Failed to load table: "
                f"{table}"
            )

            print(
                f"Error: {error}\n"
            )

            traceback.print_exc()

            self.audit_rows.append({
                "table": table,
                "source_rows":
                    source_rows
                    if "source_rows" in locals()
                    else 0,
                "loaded_rows": 0,
                "status":
                    f"FAILED: {error}"
            })

    # -------------------------------------------------
    # Save Audit & Validation Reports
    # -------------------------------------------------

    def save_reports(self):

        # Load Audit
        audit_file = (
            OUTPUT_PATH /
            "load_audit.csv"
        )

        pd.DataFrame(
            self.audit_rows
        ).to_csv(
            audit_file,
            index=False
        )

        print(
            f"\n✅ Load audit saved: "
            f"{audit_file}"
        )

        # Validation Failures
        if self.rejected_rows:

            rejected = pd.concat(
                self.rejected_rows,
                ignore_index=True,
                sort=False
            )

            validation_file = (
                OUTPUT_PATH /
                "validation_failures.csv"
            )

            rejected.to_csv(
                validation_file,
                index=False
            )

            print(
                f"⚠ Validation failures saved: "
                f"{validation_file}"
            )

    # -------------------------------------------------
    # Run Full ETL
    # -------------------------------------------------

    def run(self):

        for config in TABLES:

            self.load_table(
                config
            )

        self.save_reports()

        print(
            "\n" +
            "=" * 60
        )

        print(
            "Sprint 1 Day 05 ETL Finished"
        )

        print(
            "=" * 60
        )

    # -------------------------------------------------
    # Close Connection
    # -------------------------------------------------

    def close(self):

        self.conn.close()


# =====================================================
# Main
# =====================================================

def main():

    loader = DatabaseLoader()

    try:

        loader.run()

    finally:

        loader.close()


if __name__ == "__main__":

    main()