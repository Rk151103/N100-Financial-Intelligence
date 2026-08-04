import streamlit as st
import plotly.express as px

from src.dashboard.utils.db import get_companies

st.title("🏠 Home Dashboard")

df = get_companies()

# KPI Metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Companies",
        len(df)
    )

with col2:
    st.metric(
        "Average ROE",
        f"{df['return_on_equity_pct'].mean():.2f}%"
    )

with col3:
    st.metric(
        "Debt-Free Companies",
        (df["debt_to_equity"] <= 0).sum()
    )

st.divider()

st.subheader("Sector Distribution")

sector_df = (
    df.groupby("broad_sector")
      .size()
      .reset_index(name="Companies")
)

fig = px.pie(
    sector_df,
    values="Companies",
    names="broad_sector",
    hole=0.5,
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Top 5 Quality Companies")

top5 = (
    df.sort_values(
        "composite_quality_score",
        ascending=False
    )
    .head(5)
)

st.dataframe(
    top5[
        [
            "company_name",
            "broad_sector",
            "return_on_equity_pct",
            "composite_quality_score",
            "quality_label",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)