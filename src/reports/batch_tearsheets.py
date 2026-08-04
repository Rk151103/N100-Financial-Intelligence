"""
Sprint 5 - Day 34
Batch Company Tearsheet Generator
"""

from src.reports.company_report import CompanyReportGenerator
from src.reports.company_tearsheet import CompanyTearsheet


class BatchTearsheetGenerator:

    def __init__(self):
        self.report_generator = CompanyReportGenerator()
        self.tearsheet = CompanyTearsheet()

    def generate_all(self):

        companies = self.report_generator.generate()

        generated = 0
        failed = 0

        for _, row in companies.iterrows():

            try:

                self.tearsheet.generate(
                    row["company_name"]
                )

                generated += 1

            except Exception as e:

                failed += 1

                print(
                    f"Failed : {row['company_name']} -> {e}"
                )

        print("\n" + "=" * 50)
        print("Batch PDF Generation Completed")
        print("=" * 50)
        print(f"Generated : {generated}")
        print(f"Failed    : {failed}")


if __name__ == "__main__":
    BatchTearsheetGenerator().generate_all()