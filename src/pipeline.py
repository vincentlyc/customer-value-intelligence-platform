"""Transformation pipeline for customer-level mart and summaries."""

import pandas as pd

from config import DATA_DIR, OUTPUT_DIR


def assign_segment(row: pd.Series) -> str:
    """Assign business segment by value, frequency, and recency heuristics."""
    if row["total_revenue"] >= 25000 and row["frequency"] >= 12:
        return "VIP"
    if row["total_revenue"] >= 12000 and row["frequency"] >= 8:
        return "Loyal"
    if row["recency_days"] > 180 and row["frequency"] <= 3:
        return "At Risk"
    if row["frequency"] <= 2:
        return "New"
    return "Growth"


def churn_risk(row: pd.Series) -> str:
    """Classify churn risk from recency days."""
    if row["recency_days"] > 240:
        return "High"
    if row["recency_days"] > 120:
        return "Medium"
    return "Low"


def build_customer_mart() -> pd.DataFrame:
    """Build customer mart with RFM-style features and labels."""
    customers = pd.read_csv(DATA_DIR / "customers.csv", parse_dates=["join_date"])
    txns = pd.read_csv(DATA_DIR / "transactions.csv", parse_dates=["transaction_date"])

    ref_date = txns["transaction_date"].max() + pd.Timedelta(days=1)

    agg = (
        txns.groupby("customer_id")
        .agg(
            total_revenue=("amount", "sum"),
            frequency=("transaction_id", "count"),
            avg_order_value=("amount", "mean"),
            last_purchase_date=("transaction_date", "max"),
            favorite_channel=(
                "channel",
                lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0],
            ),
            primary_store=(
                "store",
                lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0],
            ),
        )
        .reset_index()
    )

    agg["recency_days"] = (ref_date - agg["last_purchase_date"]).dt.days
    agg["segment"] = agg.apply(assign_segment, axis=1)
    agg["churn_risk"] = agg.apply(churn_risk, axis=1)

    mart = customers.merge(agg, on="customer_id", how="left")
    mart["total_revenue"] = mart["total_revenue"].fillna(0)
    mart["frequency"] = mart["frequency"].fillna(0)
    mart["avg_order_value"] = mart["avg_order_value"].fillna(0)
    mart["recency_days"] = mart["recency_days"].fillna(999)
    mart["segment"] = mart["segment"].fillna("Dormant")
    mart["churn_risk"] = mart["churn_risk"].fillna("High")
    mart["favorite_channel"] = mart["favorite_channel"].fillna("N/A")
    mart["primary_store"] = mart["primary_store"].fillna(mart["home_store"])

    return mart


def build_summary_tables(mart: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build segment and store summary tables."""
    segment_summary = mart.groupby("segment", as_index=False).agg(
        customers=("customer_id", "count"),
        total_revenue=("total_revenue", "sum"),
        avg_revenue=("total_revenue", "mean"),
    )
    store_summary = mart.groupby("primary_store", as_index=False).agg(
        customers=("customer_id", "count"),
        total_revenue=("total_revenue", "sum"),
    )
    return segment_summary, store_summary


def main() -> None:
    """CLI entrypoint to run mart + summaries pipeline."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    mart = build_customer_mart()
    segment_summary, store_summary = build_summary_tables(mart)

    mart.to_csv(OUTPUT_DIR / "customer_mart.csv", index=False)
    segment_summary.to_csv(OUTPUT_DIR / "segment_summary.csv", index=False)
    store_summary.to_csv(OUTPUT_DIR / "store_summary.csv", index=False)
    print("Pipeline completed. Outputs saved to ./outputs")


if __name__ == "__main__":
    main()
