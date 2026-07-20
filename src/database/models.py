"""
src/database/models.py

Database Models
N100 Financial Intelligence Platform
"""

from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------
# Company
# ---------------------------------------------------------

@dataclass
class Company:
    id: str
    company_name: str
    company_logo: Optional[str] = None
    website: Optional[str] = None
    book_value: float = 0.0
    roe_percentage: float = 0.0
    roce_percentage: float = 0.0


# ---------------------------------------------------------
# Profit & Loss
# ---------------------------------------------------------

@dataclass
class ProfitLoss:
    company_id: str
    year: str
    sales: float
    expenses: float
    operating_profit: float
    net_profit: float
    eps: float


# ---------------------------------------------------------
# Balance Sheet
# ---------------------------------------------------------

@dataclass
class BalanceSheet:
    company_id: str
    year: str
    equity_capital: float
    reserves: float
    borrowings: float
    total_liabilities: float
    total_assets: float


# ---------------------------------------------------------
# Cash Flow
# ---------------------------------------------------------

@dataclass
class CashFlow:
    company_id: str
    year: str
    operating_activity: float
    investing_activity: float
    financing_activity: float
    net_cash_flow: float


# ---------------------------------------------------------
# Market Cap
# ---------------------------------------------------------

@dataclass
class MarketCap:
    company_id: str
    year: str
    market_cap_crore: float
    enterprise_value_crore: float
    pe_ratio: float
    pb_ratio: float
    ev_ebitda: float
    dividend_yield_pct: float


# ---------------------------------------------------------
# Financial Ratios
# ---------------------------------------------------------

@dataclass
class FinancialRatio:
    company_id: str
    year: str
    roe: float
    roa: float
    debt_equity: float
    current_ratio: float
    net_profit_margin: float