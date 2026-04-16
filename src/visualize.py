"""Render presentation-ready charts from processed outputs."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.config import DATA_DIR, OUTPUT_DIR

plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "Arial", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def render_charts(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR) -> None:
    """Generate summary charts and write PNG files to outputs directory."""
    output_dir.mkdir(parents=True, exist_ok=True)

    mart = pd.read_csv(output_dir / "customer_mart.csv")
    txns = pd.read_csv(data_dir / "transactions.csv", parse_dates=["transaction_date"])
    campaigns = pd.read_csv(data_dir / "campaigns.csv")

    seg = (
        mart.groupby("segment", as_index=False)["total_revenue"]
        .sum()
        .sort_values("total_revenue", ascending=False)
    )
    plt.figure(figsize=(10, 6))
    plt.bar(seg["segment"], seg["total_revenue"])
    plt.title("Revenue by Segment")
    plt.xlabel("Segment")
    plt.ylabel("Revenue")
    plt.tight_layout()
    plt.savefig(output_dir / "revenue_by_segment.png", dpi=160)
    plt.close()

    monthly = (
        txns.assign(month=txns["transaction_date"].dt.to_period("M").astype(str))
        .groupby("month", as_index=False)["amount"]
        .sum()
    )
    plt.figure(figsize=(12, 6))
    plt.plot(monthly["month"], monthly["amount"])
    plt.title("Monthly Revenue Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.xticks(rotation=60)
    plt.tight_layout()
    plt.savefig(output_dir / "monthly_revenue_trend.png", dpi=160)
    plt.close()

    plt.figure(figsize=(10, 6))
    plt.hist(mart["total_revenue"], bins=30)
    plt.title("Customer Value Distribution")
    plt.xlabel("Total Revenue")
    plt.ylabel("Customer Count")
    plt.tight_layout()
    plt.savefig(output_dir / "customer_value_distribution.png", dpi=160)
    plt.close()

    channel_perf = campaigns.groupby("channel", as_index=False)[
        ["open_rate", "conversion_rate"]
    ].mean()
    plt.figure(figsize=(10, 6))
    plt.plot(channel_perf["channel"], channel_perf["open_rate"], marker="o", label="Open Rate")
    plt.plot(
        channel_perf["channel"],
        channel_perf["conversion_rate"],
        marker="o",
        label="Conversion Rate",
    )
    plt.title("Campaign Channel Performance")
    plt.xlabel("Channel")
    plt.ylabel("Rate")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "campaign_channel_performance.png", dpi=160)
    plt.close()


def parse_args() -> argparse.Namespace:
    """Build CLI parser for chart rendering."""
    parser = argparse.ArgumentParser(description="Render analytics charts from CSV outputs.")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser.parse_args()


def main() -> None:
    """CLI entrypoint for chart rendering."""
    args = parse_args()
    render_charts(data_dir=args.data_dir, output_dir=args.output_dir)
    print(f"Charts generated in {args.output_dir}")


if __name__ == "__main__":
    main()
