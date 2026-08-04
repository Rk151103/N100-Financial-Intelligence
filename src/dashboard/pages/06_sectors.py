import streamlit as st
import plotly.express as px

from src.dashboard.utils.db import get_sectors

st.title("🏭 Sector Analysis")

sector_df = get_sectors()

st.dataframe(
    sector_df,
    use_container_width=True,
    hide_index=True,
)

fig = px.bar(
    sector_df,
    x="broad_sector",
    y="average_quality_score",
    title="Sector Quality Scores",
)

st.plotly_chart(fig, use_container_width=True)