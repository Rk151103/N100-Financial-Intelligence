"""
src/etl/validator.py

N100 Financial Intelligence Platform
Sprint 1 - Data Quality Validator

Implements reusable validation functions for ETL data quality checks.
"""

import pandas as pd


class DataValidator:

    def __init__(self):
        self.errors = []

    # =====================================================
    # Basic Validation Methods
    # =====================================================

    def validate_empty(self, df, table_name):
        """
        Check whether a dataset is empty.
        """

        if df.empty:
            self.errors.append(
                f"{table_name}: Dataset is empty"
            )

    def validate_columns(self, df, required_columns):
        """
        Check whether required columns exist.
        """

        missing = []

        for col in required_columns:
            if col not in df.columns:
                missing.append(col)

        if missing:
            self.errors.append(
                f"Missing Columns: {missing}"
            )

    def validate_duplicate_keys(self, df, keys):
        """
        DQ-01 / DQ-02
        Check duplicate primary or composite keys.
        """

        if not all(key in df.columns for key in keys):
            return

        duplicates = df.duplicated(
            subset=keys,
            keep=False
        ).sum()

        if duplicates > 0:
            self.errors.append(
                f"Duplicate Key Records : {duplicates}"
            )

    def validate_positive(self, df, column):
        """
        Check that values are positive.
        Used for DQ-06 Positive Sales.
        """

        if column not in df.columns:
            return

        numeric = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        invalid = (numeric <= 0).sum()

        if invalid > 0:
            self.errors.append(
                f"{column} has {invalid} invalid values"
            )

    def validate_nulls(self, df):
        """
        Check NULL values.
        """

        nulls = df.isnull().sum()

        for column, count in nulls.items():

            if count > 0:
                self.errors.append(
                    f"{column} contains {count} NULL values"
                )

    # =====================================================
    # DQ-01 — Primary Key Uniqueness
    # =====================================================

    def dq01_primary_key_unique(self, df, key="id"):

        if key not in df.columns:
            return

        duplicates = df.duplicated(
            subset=[key],
            keep=False
        ).sum()

        if duplicates > 0:
            self.errors.append(
                f"DQ-01 CRITICAL: {duplicates} duplicate primary keys"
            )

    # =====================================================
    # DQ-02 — Company-Year Composite Key
    # =====================================================

    def dq02_company_year_unique(self, df):

        required = ["company_id", "year"]

        if not all(col in df.columns for col in required):
            return

        duplicates = df.duplicated(
            subset=required,
            keep=False
        ).sum()

        if duplicates > 0:
            self.errors.append(
                f"DQ-02 CRITICAL: {duplicates} duplicate company-year records"
            )

    # =====================================================
    # DQ-03 — Foreign Key Integrity
    # =====================================================

    def dq03_foreign_key_integrity(
        self,
        df,
        valid_company_ids
    ):

        if "company_id" not in df.columns:
            return

        invalid = df[
            ~df["company_id"].isin(valid_company_ids)
        ]

        if len(invalid) > 0:
            self.errors.append(
                f"DQ-03 CRITICAL: {len(invalid)} invalid foreign key records"
            )

    # =====================================================
    # DQ-04 — Balance Sheet Balance
    # =====================================================

    def dq04_balance_sheet_balance(self, df):
        """
        Check whether total liabilities and total assets
        differ by more than 1%.
        """

        required = [
            "total_liabilities",
            "total_assets"
        ]

        if not all(col in df.columns for col in required):
            return

        liabilities = pd.to_numeric(
            df["total_liabilities"],
            errors="coerce"
        )

        assets = pd.to_numeric(
            df["total_assets"],
            errors="coerce"
        )

        denominator = assets.abs().replace(0, pd.NA)

        difference_pct = (
            (liabilities - assets).abs()
            / denominator
        ) * 100

        invalid = (difference_pct > 1).sum()

        if invalid > 0:
            self.errors.append(
                f"DQ-04 WARNING: {invalid} balance sheet mismatches"
            )

    # =====================================================
    # DQ-05 — OPM Cross Check
    # =====================================================

    def dq05_opm_cross_check(self, df):
        """
        Compare calculated OPM against source OPM.
        """

        required = [
            "sales",
            "operating_profit",
            "opm_percentage"
        ]

        if not all(col in df.columns for col in required):
            return

        sales = pd.to_numeric(
            df["sales"],
            errors="coerce"
        )

        operating_profit = pd.to_numeric(
            df["operating_profit"],
            errors="coerce"
        )

        source_opm = pd.to_numeric(
            df["opm_percentage"],
            errors="coerce"
        )

        calculated_opm = (
            operating_profit
            / sales.replace(0, pd.NA)
        ) * 100

        difference = (
            calculated_opm - source_opm
        ).abs()

        invalid = (difference > 1).sum()

        if invalid > 0:
            self.errors.append(
                f"DQ-05 WARNING: {invalid} OPM mismatches"
            )

    # =====================================================
    # DQ-06 — Positive Sales
    # =====================================================

    def dq06_positive_sales(self, df):

        if "sales" not in df.columns:
            return

        sales = pd.to_numeric(
            df["sales"],
            errors="coerce"
        )

        invalid = (sales <= 0).sum()

        if invalid > 0:
            self.errors.append(
                f"DQ-06 WARNING: {invalid} non-positive sales records"
            )

    # =====================================================
    # Additional Data Quality Rules
    # =====================================================

    # DQ-07 — Net Cash Flow Check

    def dq07_net_cash_flow(self, df):

        required = [
            "operating_activity",
            "investing_activity",
            "financing_activity",
            "net_cash_flow"
        ]

        if not all(col in df.columns for col in required):
            return

        calculated = (
            pd.to_numeric(
                df["operating_activity"],
                errors="coerce"
            )
            + pd.to_numeric(
                df["investing_activity"],
                errors="coerce"
            )
            + pd.to_numeric(
                df["financing_activity"],
                errors="coerce"
            )
        )

        actual = pd.to_numeric(
            df["net_cash_flow"],
            errors="coerce"
        )

        invalid = (
            (calculated - actual).abs() > 1
        ).sum()

        if invalid > 0:
            self.errors.append(
                f"DQ-07 WARNING: {invalid} net cash flow mismatches"
            )

    # DQ-08 — Tax Rate Range

    def dq08_tax_rate(self, df):

        if "tax_percentage" not in df.columns:
            return

        tax = pd.to_numeric(
            df["tax_percentage"],
            errors="coerce"
        )

        invalid = (
            (tax < 0) |
            (tax > 100)
        ).sum()

        if invalid > 0:
            self.errors.append(
                f"DQ-08 WARNING: {invalid} invalid tax rates"
            )

    # DQ-09 — Dividend Payout Range

    def dq09_dividend_payout(self, df):

        if "dividend_payout" not in df.columns:
            return

        dividend = pd.to_numeric(
            df["dividend_payout"],
            errors="coerce"
        )

        invalid = (
            (dividend < 0) |
            (dividend > 100)
        ).sum()

        if invalid > 0:
            self.errors.append(
                f"DQ-09 WARNING: {invalid} invalid dividend payout values"
            )

    # DQ-10 — EPS Sign Consistency

    def dq10_eps_sign(self, df):

        required = [
            "eps",
            "net_profit"
        ]

        if not all(col in df.columns for col in required):
            return

        eps = pd.to_numeric(
            df["eps"],
            errors="coerce"
        )

        profit = pd.to_numeric(
            df["net_profit"],
            errors="coerce"
        )

        invalid = (
            ((profit > 0) & (eps < 0)) |
            ((profit < 0) & (eps > 0))
        ).sum()

        if invalid > 0:
            self.errors.append(
                f"DQ-10 WARNING: {invalid} EPS sign inconsistencies"
            )

    # DQ-11 — URL Validation

    def dq11_url_format(self, df, column="website"):

        if column not in df.columns:
            return

        values = df[column].dropna().astype(str)

        invalid = ~values.str.startswith(
            ("http://", "https://")
        )

        count = invalid.sum()

        if count > 0:
            self.errors.append(
                f"DQ-11 WARNING: {count} invalid URLs in {column}"
            )

    # DQ-12 — Year Validation

    def dq12_year_range(
        self,
        df,
        minimum_year=1990,
        maximum_year=2100
    ):

        if "year" not in df.columns:
            return

        years = pd.to_numeric(
            df["year"],
            errors="coerce"
        )

        invalid = (
            (years < minimum_year) |
            (years > maximum_year)
        ).sum()

        if invalid > 0:
            self.errors.append(
                f"DQ-12 WARNING: {invalid} invalid year values"
            )

    # DQ-13 — Required Company ID

    def dq13_company_id_not_null(self, df):

        if "company_id" not in df.columns:
            return

        invalid = df["company_id"].isnull().sum()

        if invalid > 0:
            self.errors.append(
                f"DQ-13 CRITICAL: {invalid} missing company IDs"
            )

    # DQ-14 — Total Assets Positive

    def dq14_total_assets(self, df):

        if "total_assets" not in df.columns:
            return

        assets = pd.to_numeric(
            df["total_assets"],
            errors="coerce"
        )

        invalid = (assets <= 0).sum()

        if invalid > 0:
            self.errors.append(
                f"DQ-14 WARNING: {invalid} non-positive total assets"
            )

    # DQ-15 — Interest Coverage Input Validation

    def dq15_interest_values(self, df):

        if "interest" not in df.columns:
            return

        interest = pd.to_numeric(
            df["interest"],
            errors="coerce"
        )

        invalid = (interest < 0).sum()

        if invalid > 0:
            self.errors.append(
                f"DQ-15 WARNING: {invalid} negative interest values"
            )

    # DQ-16 — BSE/NSE Coverage

    def dq16_market_profile_coverage(self, df):

        required = [
            "nse_profile",
            "bse_profile"
        ]

        if not all(col in df.columns for col in required):
            return

        missing_both = (
            df["nse_profile"].isnull()
            & df["bse_profile"].isnull()
        ).sum()

        if missing_both > 0:
            self.errors.append(
                f"DQ-16 WARNING: {missing_both} companies missing both NSE and BSE profiles"
            )

    # =====================================================
    # Utility Methods
    # =====================================================

    def reset(self):
        """
        Clear all validation errors.
        """

        self.errors = []

    def report(self):

        print(
            "\n========== Validation Report ==========\n"
        )

        if len(self.errors) == 0:

            print("All validations passed.")

        else:

            for error in self.errors:
                print("-", error)

        print(
            "\n=======================================\n"
        )


# =========================================================
# Local Test
# =========================================================

if __name__ == "__main__":

    sample = pd.DataFrame({

        "company_id": [
            "TCS",
            "INFY"
        ],

        "year": [
            2024,
            2024
        ],

        "sales": [
            100,
            200
        ]

    })

    validator = DataValidator()

    validator.validate_empty(
        sample,
        "profitandloss"
    )

    validator.validate_columns(
        sample,
        [
            "company_id",
            "year",
            "sales"
        ]
    )

    validator.validate_duplicate_keys(
        sample,
        [
            "company_id",
            "year"
        ]
    )

    validator.validate_positive(
        sample,
        "sales"
    )

    validator.validate_nulls(
        sample
    )

    validator.report()