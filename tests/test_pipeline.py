"""Unit tests for synthetic generation and pipeline business logic."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.generate_fake_data import generate_data
from src.pipeline import (
    assign_segment,
    build_customer_mart,
    build_summary_tables,
    churn_probability,
    churn_risk,
)


def test_assign_segment_vip() -> None:
    row = pd.Series({"total_revenue": 30000, "frequency": 15, "recency_days": 10})
    assert assign_segment(row) == "VIP"


def test_assign_segment_at_risk() -> None:
    row = pd.Series({"total_revenue": 2500, "frequency": 2, "recency_days": 260})
    assert assign_segment(row) == "At Risk"


def test_churn_risk_high() -> None:
    row = pd.Series({"recency_days": 300})
    assert churn_risk(row) == "High"


def test_churn_probability_range() -> None:
    row = pd.Series({"recency_days": 120, "frequency": 4, "total_revenue": 5000})
    score = churn_probability(row)
    assert 0.01 <= score <= 0.99


def test_generate_data_writes_expected_shapes(tmp_path: Path) -> None:
    customer_df, transaction_df, campaign_df = generate_data(
        n_customers=120,
        n_transactions=900,
        seed=7,
        output_dir=tmp_path,
    )

    assert len(customer_df) == 120
    assert len(transaction_df) == 900
    assert len(campaign_df) == 20
    assert (tmp_path / "customers.csv").exists()
    assert transaction_df["amount"].min() > 0


def test_build_customer_mart_and_summaries(tmp_path: Path) -> None:
    generate_data(n_customers=80, n_transactions=500, seed=8, output_dir=tmp_path)

    mart = build_customer_mart(data_dir=tmp_path)
    segment_summary, store_summary = build_summary_tables(mart)

    assert len(mart) == 80
    assert {
        "segment",
        "churn_probability",
        "churn_risk",
        "total_revenue",
        "recency_days",
    }.issubset(mart.columns)
    assert segment_summary["customers"].sum() == 80
    assert store_summary["customers"].sum() == 80
    assert (mart["recency_days"] >= 0).all()
