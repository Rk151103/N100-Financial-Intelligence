"""
Sprint 5 - Day 35
Portfolio Summary PDF
"""

from pathlib import Path

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate

from src.reports.portfolio_report import (
    PortfolioReportGenerator,
    DEFAULT_PORTFOLIO,
    DEFAULT_YEAR,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "output" / "pdf"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class PortfolioSummaryPDF:

    def __init__(self):
        self.generator = PortfolioReportGenerator()

    def generate(self):

        report = self.generator.generate_report(
            DEFAULT_PORTFOLIO,
            DEFAULT_YEAR,
        )

        summary = report["summary"]

        pdf_file = OUTPUT_DIR / "portfolio_summary.pdf"

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
                "<b>Portfolio Intelligence Summary</b>",
                styles["Heading1"],
            )
        )

        for key, value in summary.items():

            story.append(
                Paragraph(
                    f"<b>{key}</b>: {value}",
                    styles["BodyText"],
                )
            )

        story.append(
            Paragraph(
                "<br/><b>Portfolio Narrative</b>",
                styles["Heading2"],
            )
        )

        story.append(
            Paragraph(
                report["narrative"],
                styles["BodyText"],
            )
        )

        doc = SimpleDocTemplate(str(pdf_file))

        doc.build(story)

        print(f"Generated: {pdf_file}")


if __name__ == "__main__":
    PortfolioSummaryPDF().generate()