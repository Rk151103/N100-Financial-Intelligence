"""
src/dashboard/utils/db.py

Shared cached data access for Streamlit Dashboard
"""

from pathlib import Path

import streamlit as st

from src.reports.company_report import CompanyReportGenerator
from src.reports.sector_report import SectorReportGenerator


@st.cache_data(ttl=600)
def get_companies(financial_year="Mar 2024", market_year="2024"):
    generator = CompanyReportGenerator()

    df = generator.generate(
        financial_year=financial_year,
        market_year=market_year,
    )

    return generator.add_quality_labels(df)


@st.cache_data(ttl=600)
def get_company(company_name):
    generator = CompanyReportGenerator()

    df = generator.generate_by_name(company_name)

    return generator.add_quality_labels(df)


@st.cache_data(ttl=600)
def get_sectors(financial_year="Mar 2024", market_year="2024"):
    generator = SectorReportGenerator()

    return generator.generate(
        financial_year=financial_year,
        market_year=market_year,
    )


@st.cache_data(ttl=600)
def get_sector_companies(
    financial_year="Mar 2024",
    market_year="2024",
):
    generator = SectorReportGenerator()

    return generator.load_company_data(
        financial_year=financial_year,
        market_year=market_year,
    )