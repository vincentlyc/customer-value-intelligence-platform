"""Generate synthetic datasets for customer intelligence demo use-cases."""

import argparse

import numpy as np
import pandas as pd

from config import DATA_DIR


def generate_data(
    n_customers: int = 2000,
    n_transactions: int = 40000,
    seed: int = 42,
) -> None:
    """Generate synthetic customer, transaction, and campaign datasets."""
    rng = np.random.default_rng(seed)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    customer_ids = [f"C{str(i).zfill(5)}" for i in range(1, n_customers + 1)]
    stores = ["Taipei", "Banqiao", "Taichung", "Tainan", "Kaohsiung", "Hsinchu"]
    channels = ["App", "Web", "Store", "EDM", "SMS"]
    segments = ["VIP", "Loyal", "Growth", "At Risk", "New"]

    customer_df = pd.DataFrame(
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

    txn_dates = pd.to_datetime("2024-01-01") + pd.to_timedelta(
        rng.integers(0, 730, size=n_transactions), unit="D"
    )
    base_amount = rng.lognormal(mean=7.0, sigma=0.8, size=n_transactions)
    seasonality = np.where(pd.Series(txn_dates).dt.month.isin([6, 11, 12]), 1.18, 1.0)
    amount = np.round(base_amount * seasonality, 2)

    transaction_df = pd.DataFrame(
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

    campaign_df = pd.DataFrame(
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

    customer_df.to_csv(DATA_DIR / "customers.csv", index=False)
    transaction_df.to_csv(DATA_DIR / "transactions.csv", index=False)
    campaign_df.to_csv(DATA_DIR / "campaigns.csv", index=False)


def main() -> None:
    """CLI entrypoint for synthetic data generation."""
    parser = argparse.ArgumentParser(description="Generate synthetic demo data.")
    parser.add_argument("--customers", type=int, default=2000)
    parser.add_argument("--transactions", type=int, default=40000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    generate_data(args.customers, args.transactions, args.seed)
    print("Synthetic data generated in ./data")


if __name__ == "__main__":
    main()
