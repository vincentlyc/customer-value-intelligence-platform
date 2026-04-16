"""Streamlit demo app for customer value intelligence."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.churn_forecast import build_customer_forecast
from src.config import DATA_DIR, OUTPUT_DIR

st.set_page_config(page_title="Customer Value Intelligence", layout="wide")

st.title("Customer Value Intelligence Demo")
st.caption("Solution Architect / Business Architect decision dashboard")

mart = pd.read_csv(OUTPUT_DIR / "customer_mart.csv")
segment_summary = pd.read_csv(OUTPUT_DIR / "segment_summary.csv")
store_summary = pd.read_csv(OUTPUT_DIR / "store_summary.csv")
transactions = pd.read_csv(DATA_DIR / "transactions.csv", parse_dates=["transaction_date"])

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

st.subheader("Customer Churn Prediction Lookup")
lookup_customer_id = st.text_input("輸入顧客ID（例如 C00001）", value="").strip().upper()
if lookup_customer_id:
    customer_result = mart[mart["customer_id"] == lookup_customer_id]
    if customer_result.empty:
        st.warning(f"找不到顧客ID：{lookup_customer_id}")
    else:
        target = customer_result.iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Predicted Churn Probability", f"{target['churn_probability'] * 100:.1f}%")
        c2.metric("Churn Risk Level", target["churn_risk"])
        c3.metric("Segment", target["segment"])

        customer_txns = transactions[transactions["customer_id"] == lookup_customer_id].copy()
        stats_1, stats_2, stats_3, stats_4 = st.columns(4)
        stats_1.metric("Transactions", f"{len(customer_txns):,}")
        stats_2.metric("Lifetime Revenue", f"{customer_txns['amount'].sum():,.0f}")
        stats_3.metric(
            "Average Order Value",
            f"{customer_txns['amount'].mean():,.1f}" if not customer_txns.empty else "0.0",
        )
        forecast = build_customer_forecast(
            customer_txns=customer_txns,
            current_probability=float(target["churn_probability"]),
            recency_days=float(target["recency_days"]),
            fallback_aov=float(target["avg_order_value"]),
        )
        stats_4.metric("Predicted 3M LTV", f"{forecast.predicted_ltv_3m:,.0f}")

        st.dataframe(
            customer_result[
                [
                    "customer_id",
                    "total_revenue",
                    "frequency",
                    "recency_days",
                    "avg_order_value",
                    "primary_store",
                    "favorite_channel",
                    "churn_probability",
                    "churn_risk",
                ]
            ],
            use_container_width=True,
        )
        st.subheader("Next 3 Months Churn Trend")
        st.line_chart(forecast.churn_curve, x="month_offset", y="churn_probability")

        st.subheader("Customer Transaction History")
        if customer_txns.empty:
            st.info("此顧客目前沒有交易紀錄。")
        else:
            customer_txns = customer_txns.sort_values("transaction_date", ascending=False)
            monthly = (
                customer_txns.assign(month=customer_txns["transaction_date"].dt.to_period("M").astype(str))
                .groupby("month", as_index=False)["amount"]
                .sum()
            )
            st.bar_chart(monthly, x="month", y="amount")
            st.dataframe(
                customer_txns[
                    [
                        "transaction_id",
                        "transaction_date",
                        "store",
                        "channel",
                        "category",
                        "amount",
                        "discount_rate",
                        "is_member_day",
                    ]
                ],
                use_container_width=True,
            )

st.subheader("Top Customers")
st.dataframe(
    filtered.sort_values("total_revenue", ascending=False)[
        [
            "customer_id",
            "segment",
            "churn_probability",
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
