import streamlit as st
import plotly.express as px

from src.dashboard.utils.db import get_companies

st.title("👥 Peer Comparison")

df = get_companies()

sector = st.selectbox(
    "Select Sector",
    sorted(df["broad_sector"].dropna().unique())
)

sector_df = df[df["broad_sector"] == sector]

st.subheader(f"{sector} Companies")

st.dataframe(
    sector_df[
        [
            "company_name",
            "return_on_equity_pct",
            "debt_to_equity",
            "pe_ratio",
            "composite_quality_score",
            "quality_label",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

fig = px.scatter(
    sector_df,
    x="return_on_equity_pct",
    y="pe_ratio",
    size="market_cap_crore",
    color="quality_label",
    hover_name="company_name",
    title=f"{sector} Peer Comparison",
)

st.plotly_chart(fig, use_container_width=True)