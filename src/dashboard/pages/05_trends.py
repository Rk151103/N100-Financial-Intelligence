import streamlit as st
import plotly.express as px

from src.dashboard.utils.db import get_companies

st.title("📈 Trend Analysis")

df = get_companies()

company = st.selectbox(
    "Select Company",
    sorted(df["company_name"].dropna().unique())
)

row = df[df["company_name"] == company].iloc[0]

trend_df = {
    "Metric": [
        "Revenue CAGR",
        "PAT CAGR",
        "EPS CAGR",
        "ROE",
        "Net Profit Margin",
    ],
    "Value": [
        row["revenue_cagr_5yr"],
        row["pat_cagr_5yr"],
        row["eps_cagr_5yr"],
        row["return_on_equity_pct"],
        row["net_profit_margin_pct"],
    ],
}

fig = px.bar(
    trend_df,
    x="Metric",
    y="Value",
    title=f"{company} Growth Metrics",
)

st.plotly_chart(fig, use_container_width=True)