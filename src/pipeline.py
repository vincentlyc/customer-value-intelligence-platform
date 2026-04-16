"""Transformation pipeline for customer-level mart and summaries."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.config import DATA_DIR, OUTPUT_DIR


def assign_segment(row: pd.Series) -> str:
    """Assign business segment by value, frequency, and recency heuristics."""
    revenue = float(row["total_revenue"])
    frequency = float(row["frequency"])
    recency = float(row["recency_days"])

    if revenue >= 25000 and frequency >= 12 and recency <= 60:
        return "VIP"
    if revenue >= 12000 and frequency >= 8 and recency <= 120:
        return "Loyal"
    if recency > 210 and frequency <= 3:
        return "At Risk"
    if frequency <= 2 and recency <= 90:
        return "New"
    return "Growth"


def churn_risk(row: pd.Series) -> str:
    """Classify churn risk from recency days."""
    recency_days = float(row["recency_days"])
    if recency_days > 240:
        return "High"
    if recency_days > 120:
        return "Medium"
    return "Low"


def churn_probability(row: pd.Series) -> float:
    """Estimate churn probability from RFM-style signals for demo prediction use."""
    recency_days = float(row["recency_days"])
    frequency = float(row["frequency"])
    total_revenue = float(row["total_revenue"])

    recency_score = min(recency_days / 365.0, 1.0)
    frequency_score = 1.0 - min(frequency / 20.0, 1.0)
    revenue_score = 1.0 - min(total_revenue / 30000.0, 1.0)

    score = 0.55 * recency_score + 0.30 * frequency_score + 0.15 * revenue_score
    return round(float(min(max(score, 0.01), 0.99)), 4)


def build_customer_mart(data_dir: Path = DATA_DIR) -> pd.DataFrame:
    """Build customer mart with RFM-style features and labels."""
    customers = pd.read_csv(data_dir / "customers.csv", parse_dates=["join_date"])
    txns = pd.read_csv(data_dir / "transactions.csv", parse_dates=["transaction_date"])

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
    agg["churn_probability"] = agg.apply(churn_probability, axis=1)
    agg["segment"] = agg.apply(assign_segment, axis=1)
    agg["churn_risk"] = agg.apply(churn_risk, axis=1)

    mart = customers.merge(agg, on="customer_id", how="left")
    mart["total_revenue"] = mart["total_revenue"].fillna(0)
    mart["frequency"] = mart["frequency"].fillna(0)
    mart["avg_order_value"] = mart["avg_order_value"].fillna(0)
    mart["recency_days"] = mart["recency_days"].fillna(999)
    mart["churn_probability"] = mart["churn_probability"].fillna(0.99)
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
        avg_recency_days=("recency_days", "mean"),
    )
    store_summary = mart.groupby("primary_store", as_index=False).agg(
        customers=("customer_id", "count"),
        total_revenue=("total_revenue", "sum"),
    )
    return segment_summary, store_summary


def run_pipeline(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR) -> None:
    """Run full pipeline and write all output artifacts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    mart = build_customer_mart(data_dir=data_dir)
    segment_summary, store_summary = build_summary_tables(mart)

    mart.to_csv(output_dir / "customer_mart.csv", index=False)
    segment_summary.to_csv(output_dir / "segment_summary.csv", index=False)
    store_summary.to_csv(output_dir / "store_summary.csv", index=False)


def parse_args() -> argparse.Namespace:
    """Build CLI parser for pipeline execution."""
    parser = argparse.ArgumentParser(description="Build customer intelligence mart outputs.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DATA_DIR,
        help="Input data directory containing customers.csv and transactions.csv.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Output directory for mart and summary CSV files.",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entrypoint to run mart + summaries pipeline."""
    args = parse_args()
    run_pipeline(data_dir=args.data_dir, output_dir=args.output_dir)
    print(f"Pipeline completed. Outputs saved to {args.output_dir}")


if __name__ == "__main__":
    main()
