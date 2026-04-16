"""Generate synthetic datasets for customer intelligence demo use-cases."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import DATA_DIR


def _positive_int(value: str) -> int:
    """Argparse validator for positive integers."""
    int_value = int(value)
    if int_value <= 0:
        raise argparse.ArgumentTypeError(f"Value must be a positive integer, got {value}.")
    return int_value


def _build_customers(
    rng: np.random.Generator,
    n_customers: int,
    stores: list[str],
    channels: list[str],
    segments: list[str],
) -> pd.DataFrame:
    """Create a synthetic customer master table."""
    customer_ids = [f"C{str(i).zfill(5)}" for i in range(1, n_customers + 1)]
    return pd.DataFrame(
        {
            "customer_id": customer_ids,
            "age": rng.integers(20, 66, size=n_customers),
            "gender": rng.choice(["F", "M"], size=n_customers, p=[0.58, 0.42]),
            "home_store": rng.choice(stores, size=n_customers),
            "acquisition_channel": rng.choice(
                channels,
                size=n_customers,
                p=[0.25, 0.22, 0.28, 0.15, 0.10],
            ),
            "join_date": pd.to_datetime("2023-01-01")
            + pd.to_timedelta(rng.integers(0, 800, size=n_customers), unit="D"),
            "initial_segment": rng.choice(
                segments,
                size=n_customers,
                p=[0.08, 0.22, 0.28, 0.20, 0.22],
            ),
        }
    )


def _build_transactions(
    rng: np.random.Generator,
    n_transactions: int,
    customer_ids: list[str],
    stores: list[str],
    channels: list[str],
) -> pd.DataFrame:
    """Create a synthetic transaction fact table with seasonal spend effects."""
    txn_dates = pd.to_datetime("2024-01-01") + pd.to_timedelta(
        rng.integers(0, 730, size=n_transactions), unit="D"
    )
    base_amount = rng.lognormal(mean=7.0, sigma=0.8, size=n_transactions)
    seasonality = np.where(pd.Series(txn_dates).dt.month.isin([6, 11, 12]), 1.18, 1.0)
    amount = np.round(base_amount * seasonality, 2)

    return pd.DataFrame(
        {
            "transaction_id": [f"T{str(i).zfill(7)}" for i in range(1, n_transactions + 1)],
            "customer_id": rng.choice(customer_ids, size=n_transactions),
            "transaction_date": txn_dates,
            "store": rng.choice(stores, size=n_transactions),
            "channel": rng.choice(
                channels,
                size=n_transactions,
                p=[0.20, 0.24, 0.31, 0.15, 0.10],
            ),
            "category": rng.choice(
                ["Beauty", "Fashion", "Food", "Home", "Sports"],
                size=n_transactions,
            ),
            "amount": amount,
            "discount_rate": np.round(
                rng.choice(
                    [0, 0.05, 0.1, 0.15, 0.2],
                    size=n_transactions,
                    p=[0.25, 0.20, 0.25, 0.20, 0.10],
                ),
                2,
            ),
            "is_member_day": rng.choice([0, 1], size=n_transactions, p=[0.88, 0.12]),
        }
    )


def _build_campaigns(
    rng: np.random.Generator,
    segments: list[str],
) -> pd.DataFrame:
    """Create synthetic campaign response data."""
    return pd.DataFrame(
        {
            "campaign_id": [f"MKT{str(i).zfill(4)}" for i in range(1, 21)],
            "campaign_name": [f"Campaign_{i}" for i in range(1, 21)],
            "channel": rng.choice(["EDM", "SMS", "App"], size=20),
            "launch_date": pd.to_datetime("2025-01-01")
            + pd.to_timedelta(rng.integers(0, 365, size=20), unit="D"),
            "target_segment": rng.choice(segments, size=20),
            "open_rate": np.round(rng.uniform(0.18, 0.62, size=20), 4),
            "conversion_rate": np.round(rng.uniform(0.01, 0.14, size=20), 4),
        }
    )


def generate_data(
    n_customers: int = 2000,
    n_transactions: int = 40000,
    seed: int = 42,
    output_dir: Path = DATA_DIR,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Generate and persist synthetic customer, transaction, and campaign datasets."""
    if n_customers <= 0 or n_transactions <= 0:
        raise ValueError("n_customers and n_transactions must both be positive.")

    rng = np.random.default_rng(seed)
    output_dir.mkdir(parents=True, exist_ok=True)

    stores = ["Taipei", "Banqiao", "Taichung", "Tainan", "Kaohsiung", "Hsinchu"]
    channels = ["App", "Web", "Store", "EDM", "SMS"]
    segments = ["VIP", "Loyal", "Growth", "At Risk", "New"]

    customer_df = _build_customers(rng, n_customers, stores, channels, segments)
    transaction_df = _build_transactions(
        rng,
        n_transactions,
        customer_df["customer_id"].tolist(),
        stores,
        channels,
    )
    campaign_df = _build_campaigns(rng, segments)

    customer_df.to_csv(output_dir / "customers.csv", index=False)
    transaction_df.to_csv(output_dir / "transactions.csv", index=False)
    campaign_df.to_csv(output_dir / "campaigns.csv", index=False)

    return customer_df, transaction_df, campaign_df


def parse_args() -> argparse.Namespace:
    """Build CLI parser for synthetic data generation."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic customer intelligence demo data.",
    )
    parser.add_argument("--customers", type=_positive_int, default=2000)
    parser.add_argument("--transactions", type=_positive_int, default=40000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DATA_DIR,
        help="Output directory for CSV files (default: ./data).",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entrypoint for synthetic data generation."""
    args = parse_args()
    customers, transactions, campaigns = generate_data(
        n_customers=args.customers,
        n_transactions=args.transactions,
        seed=args.seed,
        output_dir=args.output_dir,
    )
    print(
        "Generated datasets:",
        f"customers={len(customers):,}",
        f"transactions={len(transactions):,}",
        f"campaigns={len(campaigns):,}",
        f"output_dir={args.output_dir}",
    )


if __name__ == "__main__":
    main()
