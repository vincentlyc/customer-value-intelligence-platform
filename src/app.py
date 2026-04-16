"""Streamlit demo app for customer value intelligence."""

import pandas as pd
import streamlit as st

from config import OUTPUT_DIR

st.set_page_config(page_title="Customer Value Intelligence", layout="wide")

st.title("Customer Value Intelligence Demo")
st.caption("Solution Architect / Business Architect demo dashboard")

mart = pd.read_csv(OUTPUT_DIR / "customer_mart.csv")
segment_summary = pd.read_csv(OUTPUT_DIR / "segment_summary.csv")
store_summary = pd.read_csv(OUTPUT_DIR / "store_summary.csv")

segments = ["All"] + sorted(mart["segment"].dropna().unique().tolist())
selected_segment = st.sidebar.selectbox("Segment", segments)

filtered = mart.copy()
if selected_segment != "All":
    filtered = filtered[filtered["segment"] == selected_segment]

c1, c2, c3 = st.columns(3)
c1.metric("Customers", f"{len(filtered):,}")
c2.metric("Revenue", f"{filtered['total_revenue'].sum():,.0f}")
c3.metric("Avg Revenue", f"{filtered['total_revenue'].mean():,.1f}")

st.subheader("Top Customers")
st.dataframe(
    filtered.sort_values("total_revenue", ascending=False)[
        [
            "customer_id",
            "segment",
            "churn_risk",
            "total_revenue",
            "frequency",
            "avg_order_value",
            "primary_store",
        ]
    ].head(20),
    use_container_width=True,
)

st.subheader("Segment Summary")
st.dataframe(segment_summary, use_container_width=True)

st.subheader("Store Summary")
st.dataframe(store_summary, use_container_width=True)
