"""
src/etl/validator.py

Sprint 1 - Day 03
Data Quality Validator
"""

import pandas as pd


class DataValidator:

    def __init__(self):
        self.errors = []

    def validate_empty(self, df, table_name):

        if df.empty:
            self.errors.append(
                f"{table_name}: Dataset is empty"
            )

    def validate_columns(self, df, required_columns):

        missing = []

        for col in required_columns:

            if col not in df.columns:
                missing.append(col)

        if missing:
            self.errors.append(
                f"Missing Columns: {missing}"
            )

    def validate_duplicate_keys(self, df, keys):

        duplicates = df.duplicated(subset=keys).sum()

        if duplicates > 0:

            self.errors.append(
                f"Duplicate Key Records : {duplicates}"
            )

    def validate_positive(self, df, column):

        if column in df.columns:

            invalid = (df[column] <= 0).sum()

            if invalid > 0:

                self.errors.append(
                    f"{column} has {invalid} invalid values"
                )

    def validate_nulls(self, df):

        nulls = df.isnull().sum()

        for column, count in nulls.items():

            if count > 0:

                self.errors.append(
                    f"{column} contains {count} NULL values"
                )

    def report(self):

        print("\n========== Validation Report ==========\n")

        if len(self.errors) == 0:

            print("All validations passed.")

        else:

            for error in self.errors:

                print("-", error)

        print("\n=======================================\n")


if __name__ == "__main__":

    sample = pd.DataFrame({

        "company_id": ["TCS", "INFY"],

        "year": [2024, 2024],

        "sales": [100, 200]

    })

    validator = DataValidator()

    validator.validate_empty(sample, "profitandloss")

    validator.validate_columns(

        sample,

        ["company_id", "year", "sales"]

    )

    validator.validate_duplicate_keys(

        sample,

        ["company_id", "year"]

    )

    validator.validate_positive(

        sample,

        "sales"

    )

    validator.validate_nulls(sample)

    validator.report()