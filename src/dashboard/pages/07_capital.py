import streamlit as st
import plotly.express as px

from src.dashboard.utils.db import get_companies

st.title("💰 Capital Allocation")

df = get_companies()

fig = px.treemap(
    df,
    path=["broad_sector", "company_name"],
    values="market_cap_crore",
    color="composite_quality_score",
)

st.plotly_chart(fig, use_container_width=True)