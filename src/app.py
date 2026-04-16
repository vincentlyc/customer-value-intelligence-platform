"""Streamlit demo app for customer value intelligence."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.config import OUTPUT_DIR

st.set_page_config(page_title="Customer Value Intelligence", layout="wide")

st.title("Customer Value Intelligence Demo")
st.caption("Solution Architect / Business Architect decision dashboard")

mart = pd.read_csv(OUTPUT_DIR / "customer_mart.csv")
segment_summary = pd.read_csv(OUTPUT_DIR / "segment_summary.csv")
store_summary = pd.read_csv(OUTPUT_DIR / "store_summary.csv")

segments = ["All"] + sorted(mart["segment"].dropna().unique().tolist())
stores = ["All"] + sorted(mart["primary_store"].dropna().unique().tolist())

selected_segment = st.sidebar.selectbox("Segment", segments)
selected_store = st.sidebar.selectbox("Store", stores)

filtered = mart.copy()
if selected_segment != "All":
    filtered = filtered[filtered["segment"] == selected_segment]
if selected_store != "All":
    filtered = filtered[filtered["primary_store"] == selected_store]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Customers", f"{len(filtered):,}")
c2.metric("Revenue", f"{filtered['total_revenue'].sum():,.0f}")
c3.metric("Avg Revenue", f"{filtered['total_revenue'].mean():,.1f}")
c4.metric("Avg Recency", f"{filtered['recency_days'].mean():,.1f} days")

left, right = st.columns(2)
with left:
    st.subheader("Segment Revenue Mix")
    segment_chart_data = (
        filtered.groupby("segment", as_index=False)["total_revenue"].sum().sort_values("total_revenue")
    )
    st.bar_chart(segment_chart_data, x="segment", y="total_revenue", horizontal=True)

with right:
    st.subheader("Churn Risk Distribution")
    churn_dist = filtered["churn_risk"].value_counts().rename_axis("churn_risk").reset_index(name="customers")
    st.bar_chart(churn_dist, x="churn_risk", y="customers")

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
            "favorite_channel",
        ]
    ].head(20),
    use_container_width=True,
)

s1, s2 = st.columns(2)
with s1:
    st.subheader("Segment Summary")
    st.dataframe(segment_summary, use_container_width=True)
with s2:
    st.subheader("Store Summary")
    st.dataframe(store_summary, use_container_width=True)
