"""
Sprint 5 - Day 33
Company PDF Tearsheet
"""

from pathlib import Path

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
)

from src.reports.company_report import CompanyReportGenerator

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT_ROOT / "output" / "pdf"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class CompanyTearsheet:

    def __init__(self):
        self.generator = CompanyReportGenerator()

    def generate(self, company_name):

        df = self.generator.generate_by_name(company_name)

        row = df.iloc[0]

        pdf_file = OUTPUT_DIR / f"{row['company_id']}.pdf"

        doc = SimpleDocTemplate(str(pdf_file))

        styles = getSampleStyleSheet()

        story = []

        story.append(
            Paragraph(
                "<b>N100 Financial Intelligence Platform</b>",
                styles["Title"],
            )
        )

        story.append(
            Paragraph(
                f"<b>{row['company_name']}</b>",
                styles["Heading1"],
            )
        )

        story.append(
            Paragraph(
                f"Sector: {row['broad_sector']}",
                styles["BodyText"],
            )
        )

        story.append(
            Paragraph(
                f"Market Cap: ₹{row['market_cap_crore']:,.2f} Cr",
                styles["BodyText"],
            )
        )

        story.append(
            Paragraph(
                f"ROE: {row['return_on_equity_pct']}%",
                styles["BodyText"],
            )
        )

        story.append(
            Paragraph(
                f"P/E: {row['pe_ratio']}",
                styles["BodyText"],
            )
        )

        doc.build(story)

        print(f"Generated: {pdf_file}")


if __name__ == "__main__":
    CompanyTearsheet().generate("Abbott India Ltd")