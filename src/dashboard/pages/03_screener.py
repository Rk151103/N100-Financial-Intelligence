import streamlit as st
from src.dashboard.utils.db import get_companies

st.title("🔍 Company Screener")

df = get_companies()

st.sidebar.header("Filters")

min_roe = st.sidebar.slider(
    "Minimum ROE (%)",
    0.0,
    100.0,
    15.0,
)

max_de = st.sidebar.slider(
    "Maximum Debt/Equity",
    0.0,
    5.0,
    1.0,
)

min_score = st.sidebar.slider(
    "Minimum Quality Score",
    0.0,
    60.0,
    20.0,
)

filtered = df[
    (df["return_on_equity_pct"] >= min_roe)
    &
    (df["debt_to_equity"] <= max_de)
    &
    (df["composite_quality_score"] >= min_score)
]

st.success(f"{len(filtered)} companies found")

st.dataframe(
    filtered[
        [
            "company_id",
            "company_name",
            "broad_sector",
            "return_on_equity_pct",
            "debt_to_equity",
            "composite_quality_score",
            "quality_label",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download CSV",
    csv,
    "screener.csv",
    "text/csv",
)