import streamlit as st
import plotly.express as px

from src.dashboard.utils.db import get_companies

st.title("🏢 Company Profile")

df = get_companies()

company = st.selectbox(
    "Select Company",
    sorted(df["company_name"].dropna().unique())
)

selected = df[df["company_name"] == company].iloc[0]

st.subheader(company)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("ROE", f"{selected['return_on_equity_pct']:.2f}%")

with col2:
    st.metric("P/E", f"{selected['pe_ratio']:.2f}")

with col3:
    st.metric("Quality Score", f"{selected['composite_quality_score']:.2f}")

st.divider()

st.write(f"**Sector:** {selected['broad_sector']}")
st.write(f"**Sub Sector:** {selected['sub_sector']}")
st.write(f"**Market Cap:** ₹{selected['market_cap_crore']:,.2f} Cr")

chart_df = selected[
    [
        "return_on_equity_pct",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "debt_to_equity",
    ]
].to_frame(name="Value").reset_index()

chart_df.columns = ["Metric", "Value"]

fig = px.bar(
    chart_df,
    x="Metric",
    y="Value",
    title="Financial Metrics",
)

st.plotly_chart(fig, use_container_width=True)