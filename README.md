# N100 Financial Intelligence Platform
# N100 Financial Intelligence Platform

## Overview

The N100 Financial Intelligence Platform is an end-to-end financial analytics platform built for analysing Nifty 100 companies using financial statements, market data, valuation, portfolio intelligence, NLP and interactive dashboards.

## Features

### Data Engineering
- ETL Pipeline
- Data Cleaning
- SQLite Database
- Data Validation

### Financial Analytics
- Financial Ratio Engine
- CAGR Analysis
- Company Intelligence
- Peer Comparison
- Sector Analysis
- Valuation Analytics
- Cash Flow Intelligence

### Streamlit Dashboard
- Home Dashboard
- Company Intelligence
- Screener
- Peer Comparison
- Trend Analysis
- Sector Analysis
- Capital Allocation
- Reports

### NLP
- Analysis Parser
- Pros & Cons Generator
- Confidence Scoring

### Reports
- Company Intelligence Report
- Sector Report
- Portfolio Report
- Company PDF Tearsheet
- Batch PDF Generation
- Portfolio Summary PDF

## Technologies

- Python 3.14
- Pandas
- NumPy
- SQLite
- Streamlit
- Plotly
- ReportLab
- OpenPyXL

## Project Structure

```
N100-Financial-Intelligence
ÃÄÄ config
ÃÄÄ data
ÃÄÄ db
ÃÄÄ docs
ÃÄÄ notebooks
ÃÄÄ output
ÃÄÄ src
³   ÃÄÄ analytics
³   ÃÄÄ dashboard
³   ÃÄÄ database
³   ÃÄÄ etl
³   ÃÄÄ nlp
³   ÃÄÄ reports
³   ÃÄÄ screener
³   ÀÄÄ utils
ÃÄÄ tests
ÃÄÄ README.md
ÀÄÄ requirements.txt
```

## Installation

```bash
pip install -r requirements.txt
```

## Run Dashboard

```bash
python -m streamlit run src/dashboard/app.py
```

## Generate Reports

Company Tearsheet

```bash
python -m src.reports.company_tearsheet
```

Batch PDF Generation

```bash
python -m src.reports.batch_tearsheets
```

Portfolio Summary PDF

```bash
python -m src.reports.portfolio_summary_pdf
```

## Outputs

- Company Intelligence Report
- Dashboard Report
- Sector Report
- Portfolio Report
- Cash Flow Intelligence
- Capital Allocation Summary
- Pattern Changes
- Company PDF Reports
- Portfolio Summary PDF

## Sprint Progress

- ? Sprint 1 - Data Foundation
- ? Sprint 2 - Financial Ratio Engine
- ? Sprint 3 - Screener & Peer Comparison
- ? Sprint 4 - Streamlit Dashboard & Valuation
- ? Sprint 5 - NLP, PDF Reports & Intelligence

## Author

**Rakesh Kore**

B.Tech CSE (AI & ML)

Bluestock Fintech Capstone Project - N100 Financial Intelligence Platform
## Documentation

The N100 Financial Intelligence Platform documentation covers the complete development lifecycle of the project.

### Sprint 1 - Data Foundation
- ETL Pipeline
- Data Ingestion
- SQLite Database
- Data Validation

### Sprint 2 - Financial Ratio Engine
- Financial Ratios
- CAGR Analysis
- Company Intelligence
- Peer Comparison

### Sprint 3 - Screener & Intelligence
- Stock Screener
- Portfolio Intelligence
- Sector Intelligence

### Sprint 4 - Dashboard & Valuation
- Streamlit Dashboard
- Company Profile
- Trend Analysis
- Valuation Module

### Sprint 5 - NLP & Reporting
- Analysis Parser
- Pros & Cons Generator
- Cash Flow Intelligence
- Capital Allocation
- Company PDF Tearsheet
- Batch PDF Generation
- Portfolio Summary PDF
