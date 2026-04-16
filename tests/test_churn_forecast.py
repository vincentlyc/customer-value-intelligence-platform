"""Tests for customer-level churn/LTV forecast helpers."""

from __future__ import annotations

import pandas as pd

from src.churn_forecast import build_churn_curve, build_customer_forecast, predict_ltv_3m


def test_build_churn_curve_returns_three_months() -> None:
    curve = build_churn_curve(current_probability=0.3, recency_days=100, months=3)
    assert len(curve) == 3
    assert list(curve["month_offset"]) == [1, 2, 3]
    assert (curve["churn_probability"].between(0.01, 0.99)).all()


def test_predict_ltv_uses_monthly_spend_and_survival() -> None:
    txns = pd.DataFrame(
        {
            "transaction_date": pd.to_datetime(["2025-01-01", "2025-01-15", "2025-02-01", "2025-02-20"]),
            "amount": [100.0, 100.0, 200.0, 200.0],
        }
    )
    curve = pd.DataFrame({"month_offset": [1, 2, 3], "churn_probability": [0.2, 0.25, 0.3]})
    ltv, baseline = predict_ltv_3m(customer_txns=txns, churn_curve=curve, fallback_aov=50.0)
    assert baseline == 300.0
    assert ltv == 675.0


def test_build_customer_forecast_with_empty_transactions() -> None:
    txns = pd.DataFrame(columns=["transaction_date", "amount"])
    result = build_customer_forecast(
        customer_txns=txns,
        current_probability=0.5,
        recency_days=200,
        fallback_aov=120.0,
    )
    assert result.monthly_revenue_baseline == 120.0
    assert result.predicted_ltv_3m > 0
