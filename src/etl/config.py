"""
src/etl/config.py

N100 Financial Intelligence Platform
Sprint 1 - Day 05
ETL Configuration
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW = PROJECT_ROOT / "data" / "raw"

TABLES = [

    # ---------------------------------------------------------
    # Core Tables
    # ---------------------------------------------------------

    {
        "table": "companies",
        "file": RAW / "core" / "companies.xlsx",
        "header": 1,
        "drop": []
    },

    {
        "table": "sectors",
        "file": RAW / "supplementary" / "sectors.xlsx",
        "header": 0,
        "drop": ["id"]
    },

    {
        "table": "analysis",
        "file": RAW / "core" / "analysis.xlsx",
        "header": 1,
        "drop": ["id"]
    },

    {
        "table": "documents",
        "file": RAW / "core" / "documents.xlsx",
        "header": 1,
        "drop": ["id"]
    },

    {
        "table": "prosandcons",
        "file": RAW / "core" / "prosandcons.xlsx",
        "header": 1,
        "drop": ["id"]
    },

    # ---------------------------------------------------------
    # Financial Statements
    # ---------------------------------------------------------

    {
        "table": "profitandloss",
        "file": RAW / "core" / "profitandloss.xlsx",
        "header": 1,
        "drop": ["id"]
    },

    {
        "table": "balancesheet",
        "file": RAW / "core" / "balancesheet.xlsx",
        "header": 1,
        "drop": ["id"]
    },

    {
        "table": "cashflow",
        "file": RAW / "core" / "cashflow.xlsx",
        "header": 1,
        "drop": ["id"]
    },

    # ---------------------------------------------------------
    # Supplementary Tables
    # ---------------------------------------------------------

    {
        "table": "stock_prices",
        "file": RAW / "supplementary" / "stock_prices.xlsx",
        "header": 0,
        "drop": ["id"]
    },

    {
        "table": "market_cap",
        "file": RAW / "supplementary" / "market_cap.xlsx",
        "header": 0,
        "drop": ["id"]
    },

    {
        "table": "financial_ratios",
        "file": RAW / "supplementary" / "financial_ratios.xlsx",
        "header": 0,
        "drop": ["id"]
    },

    {
        "table": "peer_groups",
        "file": RAW / "supplementary" / "peer_groups.xlsx",
        "header": 0,
        "drop": ["id"]
    }

]