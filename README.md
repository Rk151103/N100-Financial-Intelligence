# N100 Financial Intelligence Platform

A modular financial intelligence and analytics platform for company analysis, sector intelligence, financial screening, ranking, portfolio analysis, risk assessment, scenario simulation, and portfolio rebalancing.

The platform transforms structured financial data into analytical insights through a Python-based data pipeline, financial analytics engines, screening models, portfolio intelligence modules, and an interactive Streamlit dashboard.

---

## Project Overview

The N100 Financial Intelligence Platform is designed to provide structured financial analysis across companies, sectors, and portfolios.

The system integrates:

- Financial data ingestion and ETL
- SQLite-based financial data storage
- Financial KPI and ratio analysis
- Company screening
- Peer comparison
- Multi-factor ranking
- Company intelligence
- Sector intelligence
- Watchlist intelligence
- Decision signal generation
- Portfolio intelligence
- Portfolio risk analysis
- Portfolio recommendations
- Scenario analysis
- Portfolio rebalancing
- CSV/report exports
- Interactive Streamlit dashboard

The project focuses on analytical financial intelligence and does not provide investment advice.

---

## Key Features

### Company Intelligence

Analyse individual companies using financial and analytical indicators.

Features include:

- Financial performance analysis
- Company intelligence scoring
- Overall ranking
- Sector ranking
- Peer comparison
- Decision signals
- Financial quality assessment

### Sector Intelligence

Analyse companies at the sector level.

Features include:

- Sector-level company comparison
- Sector ranking
- Sector performance analysis
- Sector exposure intelligence
- Cross-company analytical comparison

### Financial Screening

Screen companies using structured financial criteria and analytical metrics.

The screening system supports:

- Financial filters
- Ranking
- Presets
- Peer comparison
- Watchlist generation
- Analytical assessment

### Multi-Factor Ranking

Companies can be ranked using multiple financial and intelligence factors.

Ranking outputs support both overall and sector-level analysis.

### Watchlist Intelligence

Create analytical watchlists using company scores, assessments, rankings, and decision signals.

### Decision Signal Engine

The platform converts financial intelligence into structured analytical signals that help classify companies according to their model-derived characteristics.

---

## Portfolio Intelligence

The Portfolio Intelligence module provides portfolio-level analysis across multiple selected companies.

It supports:

- Interactive portfolio construction
- Equal weighting
- Custom portfolio weighting
- Portfolio intelligence scoring
- Portfolio health classification
- Diversification scoring
- Sector concentration analysis
- Holding-level intelligence
- Strongest and weakest holding identification
- Decision signal distribution
- Portfolio recommendations

---

## What-If Scenario Analysis

Users can compare an existing portfolio allocation against a proposed allocation without modifying the active portfolio.

Scenario comparison includes:

- Portfolio score
- Diversification score
- Average intelligence score
- Average decision score
- Concentration risk
- Largest sector exposure
- Changes between current and proposed allocations

---

## Portfolio Rebalancing

The platform includes an analytical portfolio rebalancing engine.

Users can configure:

- Weight adjustment step
- Maximum holding weight

The engine searches for alternative portfolio allocations designed to improve diversification and reduce concentration risk while evaluating portfolio intelligence metrics.

### Rebalancing Plan

The system generates holding-level actions:

- Increase
- Reduce
- Maintain

Each holding includes:

- Current weight
- Recommended weight
- Weight change
- Recommended action

### Rebalancing Action Summary

The platform summarises the proposed rebalancing plan using:

- Number of holdings to increase
- Number of holdings to reduce
- Number of holdings to maintain
- Changed holdings
- Total proposed increase
- Total proposed reduction
- Estimated portfolio turnover
- Largest proposed increase
- Largest proposed reduction
- Human-readable analytical summary

### Rebalancing Report Export

Portfolio rebalancing plans can be exported as CSV reports for further analysis.

---

## Dashboard

The project includes an interactive dashboard built using Streamlit.

Main dashboard views:

1. Company Intelligence
2. Sector Intelligence
3. Portfolio Intelligence

The dashboard provides financial metrics, tables, charts, analytical signals, portfolio construction tools, scenario analysis, rebalancing suggestions, recommendations, and exports.

---

## Technology Stack

- Python
- Pandas
- NumPy
- SQLite
- Streamlit
- Pytest
- OpenPyXL
- Git
- GitHub

---

## Project Structure

```text
N100-Financial-Intelligence/
│
├── config/
├── data/
│   ├── raw/
│   └── processed/
│
├── db/
│   └── nifty100.db
│
├── docs/
├── notebooks/
├── output/
│
├── src/
│   ├── analytics/
│   ├── database/
│   ├── dashboard/
│   ├── etl/
│   ├── reports/
│   ├── screener/
│   └── utils/
│
├── tests/
│   ├── etl/
│   ├── kpi/
│   └── screener/
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Rk151103/N100-Financial-Intelligence.git
cd N100-Financial-Intelligence
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

---

## Running the Dashboard

Start the Streamlit application:

```bash
python -m streamlit run src/dashboard/app.py
```

Then open the local address displayed by Streamlit, normally:

```text
http://localhost:8501
```

---

## Running Tests

Run the complete automated test suite:

```bash
python -m pytest
```

Current validated project status:

```text
592 passed
0 failed
```

The test suite covers the platform's ETL, analytics, screening, ranking, company intelligence, watchlist intelligence, decision signals, portfolio intelligence, recommendations, scenario analysis, rebalancing, and report-generation functionality.

---

## Current Development Status

The core N100 Financial Intelligence Platform implementation is complete through Sprint 4 Day 31.

Recent completed portfolio capabilities include:

- Interactive portfolio builder
- Custom portfolio weighting
- What-if scenario analysis
- Portfolio rebalancing suggestions
- Holding-level rebalancing plan
- Rebalancing report export
- Rebalancing action summary

Latest validated test result:

```text
592 passed
```

---

## Example Portfolio Analysis

For a sample portfolio containing:

```text
Hindustan Aeronautics Ltd    70%
Tata Consultancy Services   30%
```

the rebalancing engine produced:

```text
Recommended Allocation

Hindustan Aeronautics Ltd    50%
Tata Consultancy Services   50%

Portfolio Score
79.86 -> 80.00

Diversification
72.00 -> 80.00

Concentration Risk
High -> Moderate

Largest Sector Exposure
70% -> 50%

Estimated Portfolio Turnover
20%
```

This example demonstrates how the analytical engine evaluates allocation changes and concentration risk.

---

## Testing and Quality

The project uses automated testing with Pytest.

At the Sprint 4 Day 31 stable checkpoint:

```text
592 tests passed
```

The complete regression suite was executed successfully before the latest release commit.

---

## Disclaimer

The N100 Financial Intelligence Platform is an analytical and educational project.

Financial scores, rankings, decision signals, portfolio recommendations, scenario results, and rebalancing suggestions generated by the platform are model-derived analytical outputs.

They do not constitute investment advice, financial advice, or a recommendation to buy or sell securities.

---

## Future Enhancements

Possible future improvements include:

- Live market-data integration
- Historical portfolio backtesting
- Portfolio return analytics
- Volatility and drawdown analysis
- Advanced risk-adjusted performance metrics
- Authentication and user portfolios
- Cloud deployment
- REST API integration
- Machine-learning-based forecasting

---

## Author

**Rakesh Kore**

Computer Science Engineering — Artificial Intelligence & Machine Learning

Areas of interest:

- Artificial Intelligence
- Machine Learning
- Data Science
- Financial Analytics
- Backend Development

---

## Repository

GitHub: `Rk151103/N100-Financial-Intelligence`

---

## Project Status

**Core Development Complete — Sprint 4 Day 31**

Latest stable development commit before documentation:

```text
0f2b844
Complete Sprint 4 Day 31 portfolio rebalancing action summary
```

**Automated Tests: 592 Passed**