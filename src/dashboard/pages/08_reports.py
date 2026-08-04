import streamlit as st

from src.dashboard.utils.db import get_companies

st.title("📄 Reports")

df = get_companies()

company = st.selectbox(
    "Select Company",
    sorted(df["company_name"].dropna().unique())
)

st.write("### Company Report")

st.dataframe(
    df[df["company_name"] == company],
    use_container_width=True,
    hide_index=True,
)

csv = (
    df[df["company_name"] == company]
    .to_csv(index=False)
    .encode("utf-8")
)

st.download_button(
    "Download Report",
    csv,
    f"{company}_report.csv",
    "text/csv",
)