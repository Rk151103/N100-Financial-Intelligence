"""
src/dashboard/app.py

N100 Financial Intelligence Platform
Sprint 4 - Day 19 & Day 20

Interactive Dashboard
- Company Intelligence
- Sector Intelligence
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# =========================================================
# Project Path
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.reports.company_report import CompanyReportGenerator
from src.reports.sector_report import SectorReportGenerator
from src.screener.portfolio_intelligence import PortfolioIntelligenceEngine
from src.screener.portfolio_recommendations import PortfolioRecommendationEngine


# =========================================================
# Streamlit Configuration
# =========================================================

st.set_page_config(
    page_title="N100 Financial Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# Formatting Helpers
# =========================================================

def format_number(value, decimals=2):

    if pd.isna(value):
        return "N/A"

    try:
        return f"{float(value):,.{decimals}f}"

    except (TypeError, ValueError):
        return "N/A"


def format_percentage(value):

    if pd.isna(value):
        return "N/A"

    return f"{float(value):,.2f}%"


def format_crore(value):

    if pd.isna(value):
        return "N/A"

    return f"₹{float(value):,.2f} Cr"


# =========================================================
# Cached Data
# =========================================================

@st.cache_data
def load_company_data():

    generator = CompanyReportGenerator()

    df = generator.generate(
        financial_year="Mar 2024",
        market_year="2024",
    )

    return generator.add_quality_labels(df)


@st.cache_data
def load_sector_summary():

    generator = SectorReportGenerator()

    return generator.generate(
        financial_year="Mar 2024",
        market_year="2024",
    )


@st.cache_data
def load_sector_company_data():

    generator = SectorReportGenerator()

    return generator.load_company_data(
        financial_year="Mar 2024",
        market_year="2024",
    )


# =========================================================
# Load Data
# =========================================================

try:

    company_df = load_company_data()

    sector_summary_df = load_sector_summary()

    sector_company_df = load_sector_company_data()

except Exception as exc:

    st.error(
        f"Unable to load financial data: {exc}"
    )

    st.stop()


# =========================================================
# Header
# =========================================================

st.title("📊 N100 Financial Intelligence Platform")

st.caption(
    "Financial screening, company intelligence, "
    "sector analytics, growth analysis and quality intelligence."
)


# =========================================================
# Navigation
# =========================================================

st.sidebar.title("N100 Dashboard")

dashboard_view = st.sidebar.radio(
    "Dashboard View",
    [
        "Company Intelligence",
        "Sector Intelligence",
        "Portfolio Intelligence",
    ],
)


# =========================================================
# COMPANY INTELLIGENCE
# =========================================================

if dashboard_view == "Company Intelligence":

    st.sidebar.header("Company Filters")

    # -----------------------------------------------------
    # Sector Filter
    # -----------------------------------------------------

    sector_options = sorted(
        company_df["broad_sector"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_sector = st.sidebar.selectbox(
        "Sector",
        ["All Sectors"] + sector_options,
    )

    filtered_df = company_df.copy()

    if selected_sector != "All Sectors":

        filtered_df = filtered_df[
            filtered_df["broad_sector"]
            == selected_sector
        ].copy()

    # -----------------------------------------------------
    # Quality Filter
    # -----------------------------------------------------

    quality_options = [
        "All",
        "High Quality",
        "Moderate Quality",
        "Watchlist",
        "Unknown",
    ]

    selected_quality = st.sidebar.selectbox(
        "Quality",
        quality_options,
    )

    if selected_quality != "All":

        filtered_df = filtered_df[
            filtered_df["quality_label"]
            == selected_quality
        ].copy()

    # -----------------------------------------------------
    # Company Selection
    # -----------------------------------------------------

    company_options = (
        filtered_df["company_name"]
        .dropna()
        .sort_values()
        .tolist()
    )

    if not company_options:

        st.warning(
            "No companies match the selected filters."
        )

        st.stop()

    selected_company = st.sidebar.selectbox(
        "Company",
        company_options,
    )

    selected = filtered_df[
        filtered_df["company_name"]
        == selected_company
    ]

    if selected.empty:

        st.error(
            "Selected company data not found."
        )

        st.stop()

    company = selected.iloc[0]

    # -----------------------------------------------------
    # Company Header
    # -----------------------------------------------------

    st.header(selected_company)

    st.write(
        f"**Symbol:** "
        f"{company.get('company_id', 'N/A')}  |  "
        f"**Sector:** "
        f"{company.get('broad_sector', 'N/A')}  |  "
        f"**Sub-sector:** "
        f"{company.get('sub_sector', 'N/A')}  |  "
        f"**Quality:** "
        f"{company.get('quality_label', 'Unknown')}"
    )

    # -----------------------------------------------------
    # Main KPIs
    # -----------------------------------------------------

    st.subheader("Key Financial Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Market Cap",
            format_crore(
                company.get("market_cap_crore")
            ),
        )

    with col2:

        st.metric(
            "ROE",
            format_percentage(
                company.get(
                    "return_on_equity_pct"
                )
            ),
        )

    with col3:

        st.metric(
            "Debt / Equity",
            format_number(
                company.get(
                    "debt_to_equity"
                )
            ),
        )

    with col4:

        st.metric(
            "Quality Score",
            format_number(
                company.get(
                    "composite_quality_score"
                )
            ),
        )

    # -----------------------------------------------------
    # Valuation
    # -----------------------------------------------------

    st.subheader("Valuation")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "P/E Ratio",
            format_number(
                company.get("pe_ratio")
            ),
        )

    with col2:

        st.metric(
            "P/B Ratio",
            format_number(
                company.get("pb_ratio")
            ),
        )

    with col3:

        st.metric(
            "EV / EBITDA",
            format_number(
                company.get("ev_ebitda")
            ),
        )

    with col4:

        st.metric(
            "Dividend Yield",
            format_percentage(
                company.get(
                    "dividend_yield_pct"
                )
            ),
        )

    # -----------------------------------------------------
    # Profitability
    # -----------------------------------------------------

    st.subheader("Profitability")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Net Profit Margin",
            format_percentage(
                company.get(
                    "net_profit_margin_pct"
                )
            ),
        )

    with col2:

        st.metric(
            "Operating Margin",
            format_percentage(
                company.get(
                    "operating_profit_margin_pct"
                )
            ),
        )

    with col3:

        st.metric(
            "Asset Turnover",
            format_number(
                company.get(
                    "asset_turnover"
                )
            ),
        )

    with col4:

        st.metric(
            "Interest Coverage",
            format_number(
                company.get(
                    "interest_coverage"
                )
            ),
        )

    # -----------------------------------------------------
    # Growth
    # -----------------------------------------------------

    st.subheader("5-Year Growth")

    growth_data = pd.DataFrame(
        {
            "Metric": [
                "Revenue CAGR",
                "PAT CAGR",
                "EPS CAGR",
            ],
            "Growth (%)": [
                company.get(
                    "revenue_cagr_5yr"
                ),
                company.get(
                    "pat_cagr_5yr"
                ),
                company.get(
                    "eps_cagr_5yr"
                ),
            ],
        }
    )

    growth_chart = growth_data.dropna(
        subset=["Growth (%)"]
    )

    growth_col1, growth_col2 = st.columns(
        [1, 2]
    )

    with growth_col1:

        for _, row in growth_data.iterrows():

            st.metric(
                row["Metric"],
                format_percentage(
                    row["Growth (%)"]
                ),
            )

    with growth_col2:

        if not growth_chart.empty:

            st.bar_chart(
                growth_chart.set_index(
                    "Metric"
                )
            )

        else:

            st.info(
                "Growth history is not available."
            )

    # -----------------------------------------------------
    # Cash Flow
    # -----------------------------------------------------

    st.subheader(
        "Cash Flow & Capital Structure"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Free Cash Flow",
            format_crore(
                company.get(
                    "free_cash_flow_cr"
                )
            ),
        )

    with col2:

        st.metric(
            "Cash From Operations",
            format_crore(
                company.get(
                    "cash_from_operations_cr"
                )
            ),
        )

    with col3:

        st.metric(
            "Total Debt",
            format_crore(
                company.get(
                    "total_debt_cr"
                )
            ),
        )

    with col4:

        st.metric(
            "Capex",
            format_crore(
                company.get("capex_cr")
            ),
        )

    # -----------------------------------------------------
    # Per Share
    # -----------------------------------------------------

    st.subheader("Per Share Metrics")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "EPS",
            format_number(
                company.get(
                    "earnings_per_share"
                )
            ),
        )

    with col2:

        st.metric(
            "Book Value / Share",
            format_number(
                company.get(
                    "book_value_per_share"
                )
            ),
        )

    with col3:

        st.metric(
            "Dividend Payout",
            format_percentage(
                company.get(
                    "dividend_payout_ratio_pct"
                )
            ),
        )

    # -----------------------------------------------------
    # Sector Comparison
    # -----------------------------------------------------

    st.subheader("Sector Comparison")

    company_sector = company.get(
        "broad_sector"
    )

    peer_df = company_df[
        company_df["broad_sector"]
        == company_sector
    ].copy()

    peer_df = peer_df.sort_values(
        "composite_quality_score",
        ascending=False,
        na_position="last",
    )

    peer_columns = [
        "company_name",
        "return_on_equity_pct",
        "debt_to_equity",
        "operating_profit_margin_pct",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "composite_quality_score",
        "quality_label",
    ]

    st.dataframe(
        peer_df[peer_columns],
        use_container_width=True,
        hide_index=True,
    )

    # -----------------------------------------------------
    # N100 Ranking
    # -----------------------------------------------------

    st.subheader("N100 Quality Ranking")

    ranking_df = company_df[
        [
            "company_id",
            "company_name",
            "broad_sector",
            "return_on_equity_pct",
            "debt_to_equity",
            "composite_quality_score",
            "quality_label",
        ]
    ].copy()

    ranking_df = ranking_df.sort_values(
        "composite_quality_score",
        ascending=False,
        na_position="last",
    ).reset_index(drop=True)

    ranking_df.insert(
        0,
        "rank",
        range(
            1,
            len(ranking_df) + 1,
        ),
    )

    st.dataframe(
        ranking_df.head(25),
        use_container_width=True,
        hide_index=True,
    )

    # -----------------------------------------------------
    # Download
    # -----------------------------------------------------

    st.subheader("Export")

    csv_data = filtered_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "Download Filtered Company Data",
        data=csv_data,
        file_name=(
            "n100_company_intelligence.csv"
        ),
        mime="text/csv",
    )


# =========================================================
# SECTOR INTELLIGENCE
# =========================================================

elif dashboard_view == "Sector Intelligence":

    st.sidebar.header("Sector Filters")

    sectors = (
        sector_summary_df["broad_sector"]
        .dropna()
        .sort_values()
        .tolist()
    )

    selected_sector = st.sidebar.selectbox(
        "Select Sector",
        sectors,
    )

    # -----------------------------------------------------
    # Overall Sector Ranking
    # -----------------------------------------------------

    st.header("Sector Intelligence")

    st.caption(
        "Compare N100 sectors using quality, "
        "growth, profitability, valuation and "
        "capital structure metrics."
    )

    st.subheader("N100 Sector Ranking")

    ranking_columns = [
        "sector_rank",
        "broad_sector",
        "company_count",
        "total_market_cap_crore",
        "average_roe_pct",
        "average_debt_to_equity",
        "average_revenue_cagr_5yr",
        "average_pat_cagr_5yr",
        "average_quality_score",
    ]

    st.dataframe(
        sector_summary_df[
            ranking_columns
        ],
        use_container_width=True,
        hide_index=True,
    )

    # -----------------------------------------------------
    # Selected Sector
    # -----------------------------------------------------

    selected_summary = sector_summary_df[
        sector_summary_df["broad_sector"]
        == selected_sector
    ]

    if selected_summary.empty:

        st.error(
            "Sector information not available."
        )

        st.stop()

    sector = selected_summary.iloc[0]

    st.header(selected_sector)

    st.write(
        f"**Sector Rank:** "
        f"{int(sector['sector_rank'])} / "
        f"{len(sector_summary_df)}"
    )

    # -----------------------------------------------------
    # Sector KPIs
    # -----------------------------------------------------

    st.subheader("Sector Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Companies",
            int(
                sector["company_count"]
            ),
        )

    with col2:

        st.metric(
            "Total Market Cap",
            format_crore(
                sector[
                    "total_market_cap_crore"
                ]
            ),
        )

    with col3:

        st.metric(
            "Average Quality Score",
            format_number(
                sector[
                    "average_quality_score"
                ]
            ),
        )

    with col4:

        st.metric(
            "Average ROE",
            format_percentage(
                sector[
                    "average_roe_pct"
                ]
            ),
        )

    # -----------------------------------------------------
    # Sector Financial KPIs
    # -----------------------------------------------------

    st.subheader(
        "Sector Financial Metrics"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Average Debt / Equity",
            format_number(
                sector[
                    "average_debt_to_equity"
                ]
            ),
        )

    with col2:

        st.metric(
            "Average Revenue CAGR",
            format_percentage(
                sector[
                    "average_revenue_cagr_5yr"
                ]
            ),
        )

    with col3:

        st.metric(
            "Average PAT CAGR",
            format_percentage(
                sector[
                    "average_pat_cagr_5yr"
                ]
            ),
        )

    with col4:

        st.metric(
            "Average EPS CAGR",
            format_percentage(
                sector[
                    "average_eps_cagr_5yr"
                ]
            ),
        )

    # -----------------------------------------------------
    # Quality Comparison Chart
    # -----------------------------------------------------

    st.subheader(
        "Sector Quality Comparison"
    )

    quality_chart = (
        sector_summary_df[
            [
                "broad_sector",
                "average_quality_score",
            ]
        ]
        .sort_values(
            "average_quality_score",
            ascending=False,
        )
        .set_index("broad_sector")
    )

    st.bar_chart(
        quality_chart
    )

    # -----------------------------------------------------
    # Market Cap Comparison
    # -----------------------------------------------------

    st.subheader(
        "Sector Market Capitalisation"
    )

    market_chart = (
        sector_summary_df[
            [
                "broad_sector",
                "total_market_cap_crore",
            ]
        ]
        .sort_values(
            "total_market_cap_crore",
            ascending=False,
        )
        .set_index("broad_sector")
    )

    st.bar_chart(
        market_chart
    )

    # -----------------------------------------------------
    # Growth Comparison
    # -----------------------------------------------------

    st.subheader(
        "Sector Growth Comparison"
    )

    growth_chart = (
        sector_summary_df[
            [
                "broad_sector",
                "average_revenue_cagr_5yr",
                "average_pat_cagr_5yr",
                "average_eps_cagr_5yr",
            ]
        ]
        .set_index("broad_sector")
    )

    st.bar_chart(
        growth_chart
    )

    # -----------------------------------------------------
    # Selected Sector Companies
    # -----------------------------------------------------

    st.subheader(
        f"Top Companies — {selected_sector}"
    )

    selected_sector_companies = (
        sector_company_df[
            sector_company_df["broad_sector"]
            == selected_sector
        ]
        .copy()
        .sort_values(
            "composite_quality_score",
            ascending=False,
            na_position="last",
        )
        .reset_index(drop=True)
    )

    selected_sector_companies.insert(
        0,
        "sector_rank",
        range(
            1,
            len(
                selected_sector_companies
            ) + 1,
        ),
    )

    company_columns = [
        "sector_rank",
        "company_id",
        "company_name",
        "market_cap_crore",
        "return_on_equity_pct",
        "debt_to_equity",
        "operating_profit_margin_pct",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "composite_quality_score",
    ]

    st.dataframe(
        selected_sector_companies[
            company_columns
        ],
        use_container_width=True,
        hide_index=True,
    )

    # -----------------------------------------------------
    # Top 5 Sector Leaders
    # -----------------------------------------------------

    st.subheader("Sector Leaders")

    top_companies = (
        selected_sector_companies
        .head(5)
    )

    leader_chart = (
        top_companies[
            [
                "company_name",
                "composite_quality_score",
            ]
        ]
        .set_index("company_name")
    )

    st.bar_chart(
        leader_chart
    )

    # -----------------------------------------------------
    # Sector Valuation
    # -----------------------------------------------------

    st.subheader(
        "Sector Valuation"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Average P/E",
            format_number(
                sector[
                    "average_pe_ratio"
                ]
            ),
        )

    with col2:

        st.metric(
            "Average P/B",
            format_number(
                sector[
                    "average_pb_ratio"
                ]
            ),
        )

    with col3:

        st.metric(
            "Average Dividend Yield",
            format_percentage(
                sector[
                    "average_dividend_yield_pct"
                ]
            ),
        )

    # -----------------------------------------------------
    # Sector Cash Flow
    # -----------------------------------------------------

    st.subheader(
        "Sector Cash Flow"
    )

    st.metric(
        "Total Free Cash Flow",
        format_crore(
            sector[
                "total_free_cash_flow_cr"
            ]
        ),
    )

    # -----------------------------------------------------
    # Export
    # -----------------------------------------------------

    st.subheader("Export")

    sector_csv = (
        selected_sector_companies
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        "Download Selected Sector Data",
        data=sector_csv,
        file_name=(
            selected_sector
            .lower()
            .replace(" ", "_")
            + "_sector.csv"
        ),
        mime="text/csv",
    )

    summary_csv = (
        sector_summary_df
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        "Download Sector Intelligence Report",
        data=summary_csv,
        file_name=(
            "n100_sector_intelligence.csv"
        ),
        mime="text/csv",
    )


# =========================================================
# =========================================================
# PORTFOLIO INTELLIGENCE
# =========================================================

elif dashboard_view == "Portfolio Intelligence":

    st.header("Portfolio Intelligence")

    st.caption(
        "Portfolio-level financial intelligence, decision signals, "
        "sector concentration, risk analysis and recommendations."
    )

    # -----------------------------------------------------
    # Portfolio Configuration
    # -----------------------------------------------------

    # -----------------------------------------------------
    # Interactive Portfolio Builder
    # -----------------------------------------------------

    st.subheader("Build Your Portfolio")

    default_portfolio = [
        "HAL",
        "TCS",
        "LTIM",
        "ITC",
        "INFY",
        "HCLTECH",
        "MARUTI",
        "RELIANCE",
    ]

    # Create Company Name -> Company ID mapping
    portfolio_company_df = (
        company_df[
            ["company_id", "company_name", "broad_sector"]
        ]
        .dropna(subset=["company_id", "company_name"])
        .drop_duplicates(subset=["company_id"])
        .sort_values("company_name")
    )

    company_name_to_id = dict(
        zip(
            portfolio_company_df["company_name"],
            portfolio_company_df["company_id"],
        )
    )

    company_id_to_name = dict(
        zip(
            portfolio_company_df["company_id"],
            portfolio_company_df["company_name"],
        )
    )

    # Convert default IDs to company names
    default_company_names = [
        company_id_to_name[company_id]
        for company_id in default_portfolio
        if company_id in company_id_to_name
    ]

    selected_company_names = st.multiselect(
        "Select Portfolio Companies",
        options=portfolio_company_df["company_name"].tolist(),
        default=default_company_names,
        help=(
            "Select companies to analyse. Portfolio intelligence, "
            "risk and recommendations update automatically."
        ),
    )

    # Convert selected names back to IDs required by engines
    selected_portfolio = [
        company_name_to_id[name]
        for name in selected_company_names
    ]

    portfolio_year = "Mar 2024"

    st.caption(
        f"Selected holdings: {len(selected_portfolio)}"
    )

    if not selected_portfolio:
        st.warning(
            "Select at least one company to generate portfolio intelligence."
        )
        st.stop()

    # -----------------------------------------------------
    # Portfolio Weight Configuration
    # -----------------------------------------------------

    weight_mode = st.radio(
        "Portfolio Weighting",
        [
            "Equal Weight",
            "Custom Weight",
        ],
        horizontal=True,
        help=(
            "Equal Weight distributes the portfolio equally. "
            "Custom Weight lets you assign your own percentages."
        ),
    )

    portfolio_weights = None

    if weight_mode == "Custom Weight":
        st.markdown("#### Custom Portfolio Weights")

        st.caption(
            "Assign a percentage to each holding. "
            "The total must equal 100%."
        )

        portfolio_weights = {}

        default_weight = round(
            100.0 / len(selected_portfolio),
            2,
        )

        for company_name in selected_company_names:
            company_id = company_name_to_id[
                company_name
            ]

            portfolio_weights[company_id] = (
                st.number_input(
                    company_name,
                    min_value=0.0,
                    max_value=100.0,
                    value=default_weight,
                    step=1.0,
                    format="%.2f",
                    key=f"portfolio_weight_{company_id}",
                )
            )

        total_weight = round(
            sum(portfolio_weights.values()),
            2,
        )

        st.metric(
            "Total Portfolio Weight",
            f"{total_weight:.2f}%",
        )

        if abs(total_weight - 100.0) > 0.01:
            st.error(
                "Custom portfolio weights must total 100%. "
                f"Current total: {total_weight:.2f}%"
            )
            st.stop()

    try:
        portfolio_engine = PortfolioIntelligenceEngine()
        recommendation_engine = PortfolioRecommendationEngine()

        portfolio_df = portfolio_engine.analyse_portfolio(
            selected_portfolio,
            year=portfolio_year,
            ignore_invalid=False,
            weights=portfolio_weights,
        )

        portfolio_summary = portfolio_engine.portfolio_summary(
            selected_portfolio,
            year=portfolio_year,
            ignore_invalid=False,
            weights=portfolio_weights,
        )

        sector_allocation_df = portfolio_engine.sector_allocation(
            selected_portfolio,
            year=portfolio_year,
            ignore_invalid=False,
            weights=portfolio_weights,
        )

        signal_distribution_df = portfolio_engine.signal_distribution(
            selected_portfolio,
            year=portfolio_year,
            ignore_invalid=False,
            weights=portfolio_weights,
        )

        holding_recommendations_df = (
            recommendation_engine.holding_recommendations(
                selected_portfolio,
                year=portfolio_year,
                ignore_invalid=False,
                weights=portfolio_weights,
            )
        )

        sector_risk_df = (
            recommendation_engine.sector_risk_analysis(
                selected_portfolio,
                year=portfolio_year,
                ignore_invalid=False,
                weights=portfolio_weights,
            )
        )

        recommendations = (
            recommendation_engine.portfolio_recommendations(
                selected_portfolio,
                year=portfolio_year,
                ignore_invalid=False,
                weights=portfolio_weights,
            )
        )

        recommendation_summary = (
            recommendation_engine.recommendation_summary(
                selected_portfolio,
                year=portfolio_year,
                ignore_invalid=False,
                weights=portfolio_weights,
            )
        )

    except Exception as exc:
        st.error(
            f"Unable to load portfolio intelligence: {exc}"
        )
        st.stop()

    # -----------------------------------------------------
    # Portfolio Overview
    # -----------------------------------------------------

    st.subheader("Portfolio Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Portfolio Score",
            f"{portfolio_summary['portfolio_score']:.2f} / 100",
        )

    with col2:
        st.metric(
            "Portfolio Health",
            portfolio_summary["portfolio_health"],
        )

    with col3:
        st.metric(
            "Diversification",
            f"{portfolio_summary['diversification_score']:.2f} / 100",
        )

    with col4:
        st.metric(
            "Companies",
            portfolio_summary["company_count"],
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Average Intelligence",
            f"{portfolio_summary['average_intelligence_score']:.2f}",
        )

    with col2:
        st.metric(
            "Average Decision Score",
            f"{portfolio_summary['average_decision_score']:.2f}",
        )

    with col3:
        st.metric(
            "Sectors",
            portfolio_summary["sector_count"],
        )

    with col4:
        st.metric(
            "Concentration Risk",
            portfolio_summary["concentration_risk"],
        )

    # -----------------------------------------------------
    # Day 27 - What-If Scenario Analysis
    # -----------------------------------------------------

    st.subheader("What-If Scenario Analysis")

    st.caption(
        "Compare the current portfolio allocation with a "
        "proposed allocation without changing the active portfolio."
    )

    with st.expander(
        "Build Proposed Portfolio Scenario",
        expanded=False,
    ):
        proposed_weights = {}

        current_weight_lookup = dict(
            zip(
                portfolio_df["company_id"],
                portfolio_df["portfolio_weight_pct"],
            )
        )

        for company_name in selected_company_names:
            company_id = company_name_to_id[
                company_name
            ]

            proposed_weights[company_id] = (
                st.number_input(
                    company_name,
                    min_value=0.0,
                    max_value=100.0,
                    value=float(
                        current_weight_lookup.get(
                            company_id,
                            0.0,
                        )
                    ),
                    step=1.0,
                    format="%.2f",
                    key=f"scenario_weight_{company_id}",
                )
            )

        proposed_total = round(
            sum(proposed_weights.values()),
            2,
        )

        st.metric(
            "Proposed Portfolio Weight",
            f"{proposed_total:.2f}%",
        )

        if abs(proposed_total - 100.0) > 0.01:
            st.warning(
                "Proposed portfolio weights must total 100%. "
                f"Current total: {proposed_total:.2f}%"
            )

        else:
            try:
                scenario = portfolio_engine.compare_scenarios(
                    selected_portfolio,
                    current_weights=portfolio_weights,
                    proposed_weights=proposed_weights,
                    year=portfolio_year,
                    ignore_invalid=False,
                )

                st.markdown("#### Current vs Proposed")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Portfolio Score",
                        (
                            f"{scenario['proposed_portfolio_score']:.2f}"
                        ),
                        delta=(
                            f"{scenario['portfolio_score_change']:+.2f}"
                        ),
                    )

                with col2:
                    st.metric(
                        "Diversification",
                        (
                            f"{scenario['proposed_diversification_score']:.2f}"
                        ),
                        delta=(
                            f"{scenario['diversification_change']:+.2f}"
                        ),
                    )

                with col3:
                    st.metric(
                        "Average Decision Score",
                        (
                            f"{scenario['proposed_average_decision_score']:.2f}"
                        ),
                        delta=(
                            f"{scenario['average_decision_change']:+.2f}"
                        ),
                    )

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Average Intelligence",
                        (
                            f"{scenario['proposed_average_intelligence_score']:.2f}"
                        ),
                        delta=(
                            f"{scenario['average_intelligence_change']:+.2f}"
                        ),
                    )

                with col2:
                    st.metric(
                        "Concentration Risk",
                        scenario["proposed_concentration_risk"],
                    )

                    st.caption(
                        "Current: "
                        f"{scenario['current_concentration_risk']}"
                    )

                with col3:
                    st.metric(
                        "Largest Sector Exposure",
                        (
                            f"{scenario['proposed_largest_sector_weight_pct']:.2f}%"
                        ),
                        delta=(
                            f"{scenario['largest_sector_weight_change']:+.2f}%"
                        ),
                        delta_color="inverse",
                    )

                    st.caption(
                        "Proposed largest sector: "
                        f"{scenario['proposed_largest_sector']}"
                    )

                st.caption(
                    "Scenario results are analytical simulations "
                    "and do not constitute investment advice."
                )

            except Exception as exc:
                st.error(
                    f"Unable to analyse proposed scenario: {exc}"
                )

    # -----------------------------------------------------
    # Day 28 - Portfolio Rebalancing Suggestions
    # -----------------------------------------------------

    st.subheader("Portfolio Rebalancing Suggestions")

    st.caption(
        "Generate an analytical allocation that aims to improve "
        "portfolio diversification and reduce concentration risk."
    )

    with st.expander(
        "Generate Rebalancing Suggestion",
        expanded=False,
    ):
        col1, col2 = st.columns(2)

        with col1:
            rebalance_step = st.selectbox(
                "Weight Adjustment Step",
                options=[5, 10, 20, 25],
                index=1,
                help=(
                    "Controls the percentage increments used when "
                    "searching for alternative portfolio allocations."
                ),
            )

        with col2:
            rebalance_max_weight = st.number_input(
                "Maximum Holding Weight (%)",
                min_value=10.0,
                max_value=100.0,
                value=60.0,
                step=5.0,
                format="%.2f",
                help=(
                    "Maximum percentage that can be allocated "
                    "to any individual holding."
                ),
            )

        if st.button(
            "Generate Rebalancing Suggestion",
            key="generate_portfolio_rebalancing",
        ):
            try:
                rebalance_result = (
                    portfolio_engine.suggest_rebalanced_weights(
                        selected_portfolio,
                        current_weights=portfolio_weights,
                        year=portfolio_year,
                        ignore_invalid=False,
                        step=rebalance_step,
                        max_weight=rebalance_max_weight,
                    )
                )

                st.markdown("#### Recommended Allocation")

                rebalancing_plan = (
                    portfolio_engine.generate_rebalancing_plan(
                        selected_portfolio,
                        current_weights=portfolio_weights,
                        year=portfolio_year,
                        ignore_invalid=False,
                        step=rebalance_step,
                        max_weight=rebalance_max_weight,
                    )
                )

                display_plan = rebalancing_plan.rename(
                    columns={
                        "company_name": "Company",
                        "current_weight_pct": "Current Weight (%)",
                        "recommended_weight_pct": (
                            "Recommended Weight (%)"
                        ),
                        "weight_change_pct": "Change (%)",
                        "action": "Action",
                    }
                )

                display_columns = [
                    "Company",
                    "Current Weight (%)",
                    "Recommended Weight (%)",
                    "Change (%)",
                    "Action",
                ]

                st.dataframe(
                    display_plan[display_columns],
                    width="stretch",
                    hide_index=True,
                )

                st.markdown("#### Rebalancing Impact")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Portfolio Score",
                        (
                            f"{rebalance_result['recommended_portfolio_score']:.2f}"
                        ),
                        delta=(
                            f"{rebalance_result['portfolio_score_change']:+.2f}"
                        ),
                    )

                with col2:
                    st.metric(
                        "Diversification",
                        (
                            f"{rebalance_result['recommended_diversification_score']:.2f}"
                        ),
                        delta=(
                            f"{rebalance_result['diversification_change']:+.2f}"
                        ),
                    )

                with col3:
                    st.metric(
                        "Concentration Risk",
                        rebalance_result[
                            "recommended_concentration_risk"
                        ],
                    )

                    st.caption(
                        "Current: "
                        f"{rebalance_result['current_concentration_risk']}"
                    )

                st.metric(
                    "Largest Sector Exposure",
                    (
                        f"{rebalance_result['recommended_largest_sector_weight_pct']:.2f}%"
                    ),
                    delta=(
                        f"{rebalance_result['largest_sector_weight_change']:+.2f}%"
                    ),
                    delta_color="inverse",
                )

                st.caption(
                    "Rebalancing suggestions are analytical model "
                    "outputs and do not constitute investment advice."
                )

            except Exception as exc:
                st.error(
                    f"Unable to generate rebalancing suggestion: {exc}"
                )

    # -----------------------------------------------------
    # Portfolio Holdings
    # -----------------------------------------------------

    st.subheader("Portfolio Holdings")

    holding_columns = [
        "company_id",
        "company_name",
        "broad_sector",
        "overall_rank",
        "sector_rank",
        "intelligence_score",
        "decision_score",
        "signal",
        "portfolio_weight_pct",
    ]

    holding_columns = [
        column
        for column in holding_columns
        if column in portfolio_df.columns
    ]

    st.dataframe(
        portfolio_df[holding_columns],
        width="stretch",
        hide_index=True,
    )

    # -----------------------------------------------------
    # Strongest and Weakest Holdings
    # -----------------------------------------------------

    st.subheader("Holding Intelligence")

    col1, col2 = st.columns(2)

    with col1:
        st.success(
            f"""
**Strongest Holding**

{portfolio_summary['strongest_company_name']}

Decision Score: {portfolio_summary['strongest_decision_score']:.2f}
"""
        )

    with col2:
        st.warning(
            f"""
**Weakest Holding**

{portfolio_summary['weakest_company_name']}

Decision Score: {portfolio_summary['weakest_decision_score']:.2f}
"""
        )

    # -----------------------------------------------------
    # Sector Allocation
    # -----------------------------------------------------

    st.subheader("Sector Allocation")

    sector_col1, sector_col2 = st.columns([1, 2])

    with sector_col1:
        st.dataframe(
            sector_allocation_df,
            width="stretch",
            hide_index=True,
        )

    with sector_col2:

        if (
            not sector_allocation_df.empty
            and "broad_sector" in sector_allocation_df.columns
            and "weight_pct" in sector_allocation_df.columns
        ):
            sector_chart = sector_allocation_df.set_index(
                "broad_sector"
            )[["weight_pct"]]

            st.bar_chart(sector_chart)

    # -----------------------------------------------------
    # Decision Signal Distribution
    # -----------------------------------------------------

    st.subheader("Decision Signal Distribution")

    signal_col1, signal_col2 = st.columns([1, 2])

    with signal_col1:
        st.dataframe(
            signal_distribution_df,
            width="stretch",
            hide_index=True,
        )

    with signal_col2:

        if (
            not signal_distribution_df.empty
            and "signal" in signal_distribution_df.columns
            and "company_count" in signal_distribution_df.columns
        ):
            signal_chart = signal_distribution_df.set_index(
                "signal"
            )[["company_count"]]

            st.bar_chart(signal_chart)

    # -----------------------------------------------------
    # Holding Recommendations
    # -----------------------------------------------------

    st.subheader("Holding Recommendations")

    recommendation_columns = [
        "recommendation_rank",
        "company_id",
        "company_name",
        "decision_score",
        "signal",
        "recommended_action",
        "priority",
    ]

    recommendation_columns = [
        column
        for column in recommendation_columns
        if column in holding_recommendations_df.columns
    ]

    st.dataframe(
        holding_recommendations_df[
            recommendation_columns
        ],
        width="stretch",
        hide_index=True,
    )

    # -----------------------------------------------------
    # Recommendation Summary
    # -----------------------------------------------------

    st.subheader("Recommendation Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Maintain",
            recommendation_summary["maintain_count"],
        )

    with col2:
        st.metric(
            "Review",
            recommendation_summary["review_count"],
        )

    with col3:
        st.metric(
            "Reduce Exposure",
            recommendation_summary["reduce_exposure_count"],
        )

    with col4:
        st.metric(
            "High Priority",
            recommendation_summary["high_priority_count"],
        )

    # -----------------------------------------------------
    # Sector Risk
    # -----------------------------------------------------

    st.subheader("Sector Risk Analysis")

    st.dataframe(
        sector_risk_df,
        width="stretch",
        hide_index=True,
    )

    # -----------------------------------------------------
    # Portfolio Recommendations
    # -----------------------------------------------------

    st.subheader("Portfolio Recommendations")

    if recommendations:
        for number, recommendation in enumerate(
            recommendations,
            start=1,
        ):
            st.write(
                f"{number}. {recommendation}"
            )
    else:
        st.info(
            "No portfolio recommendations were generated."
        )

    # -----------------------------------------------------
    # Portfolio Assessment
    # -----------------------------------------------------

    st.subheader("Portfolio Assessment")

    st.write(
        f"The portfolio contains "
        f"{portfolio_summary['company_count']} companies across "
        f"{portfolio_summary['sector_count']} sectors for "
        f"{portfolio_year}. Its portfolio intelligence score is "
        f"{portfolio_summary['portfolio_score']:.2f}/100 and is "
        f"classified as "
        f"{portfolio_summary['portfolio_health']}. "
        f"The diversification score is "
        f"{portfolio_summary['diversification_score']:.2f}/100. "
        f"{portfolio_summary['largest_sector']} is the largest "
        f"sector exposure at "
        f"{portfolio_summary['largest_sector_weight_pct']:.1f}%."
    )

    st.write(
        f"Strongest holding: "
        f"**{portfolio_summary['strongest_company_name']}** "
        f"with a decision score of "
        f"{portfolio_summary['strongest_decision_score']:.2f}."
    )

    st.write(
        f"Weakest holding: "
        f"**{portfolio_summary['weakest_company_name']}** "
        f"with a decision score of "
        f"{portfolio_summary['weakest_decision_score']:.2f}."
    )

    st.info(
        "Portfolio intelligence and recommendations are analytical "
        "model outputs and are not investment advice."
    )

    # -----------------------------------------------------
    # Export
    # -----------------------------------------------------

    st.subheader("Export")

    portfolio_csv = (
        portfolio_df
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        "Download Portfolio Intelligence",
        data=portfolio_csv,
        file_name="n100_portfolio_intelligence.csv",
        mime="text/csv",
    )

    recommendation_csv = (
        holding_recommendations_df
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        "Download Portfolio Recommendations",
        data=recommendation_csv,
        file_name="n100_portfolio_recommendations.csv",
        mime="text/csv",
    )
# =========================================================
# Footer
# =========================================================

st.divider()

st.caption(
    "N100 Financial Intelligence Platform | "
    "Sprint 4 Dashboard"
)
