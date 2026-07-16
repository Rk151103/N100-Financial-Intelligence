"""
src/etl/loader.py

N100 Financial Intelligence Platform
Sprint 1 - Day 02
Excel Loader
"""

from pathlib import Path
import pandas as pd


class ExcelLoader:
    def __init__(self, data_dir="data/raw"):
        self.data_dir = Path(data_dir)

    def list_excel_files(self):
        """
        Recursively find all Excel files.
        """

        excel_files = []

        excel_files.extend(self.data_dir.rglob("*.xlsx"))
        excel_files.extend(self.data_dir.rglob("*.xls"))

        return sorted(excel_files)

    def get_header_row(self, filename):
        """
        Core datasets use header=1.
        Supplementary datasets use header=0.
        """

        core_files = {
            "companies",
            "profitandloss",
            "balancesheet",
            "cashflow",
            "analysis",
            "documents",
            "prosandcons",
        }

        if filename.lower() in core_files:
            return 1

        return 0

    def load_file(self, filepath):
        """
        Load one Excel file.
        """

        try:

            header = self.get_header_row(filepath.stem)

            df = pd.read_excel(filepath, header=header)

            print(
                f"[OK] {filepath.name:<30}"
                f"Rows: {len(df):>5}"
                f"  Cols: {len(df.columns):>3}"
            )

            return df

        except Exception as e:

            print(f"[ERROR] {filepath.name}: {e}")

            return None

    def load_all(self):
        """
        Load every Excel dataset.
        """

        datasets = {}

        excel_files = self.list_excel_files()

        if len(excel_files) == 0:
            print("\nNo Excel files found.")
            return datasets

        print("\nLoading datasets...\n")

        for file in excel_files:

            datasets[file.stem] = self.load_file(file)

        print("\n------------------------------------")
        print(f"Datasets Loaded : {len(datasets)}")
        print("------------------------------------\n")

        return datasets


if __name__ == "__main__":

    loader = ExcelLoader()

    datasets = loader.load_all()

    print("Available Datasets\n")

    for dataset_name in datasets.keys():
        print(f"• {dataset_name}")