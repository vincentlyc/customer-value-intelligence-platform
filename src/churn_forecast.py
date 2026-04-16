"""Helpers for single-customer churn and LTV demo forecasting."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class CustomerForecast:
    """Container for lookup-level forecast outputs."""

    predicted_ltv_3m: float
    monthly_revenue_baseline: float
    churn_curve: pd.DataFrame


def build_churn_curve(
    current_probability: float,
    recency_days: float,
    months: int = 3,
) -> pd.DataFrame:
    """Forecast churn probability over upcoming months with no new-purchase assumption."""
    base = float(min(max(current_probability, 0.01), 0.99))
    recency_factor = min(max(recency_days / 365.0, 0.0), 1.0)
    monthly_step = 0.02 + 0.04 * recency_factor

    probs: list[float] = []
    for i in range(1, months + 1):
        probs.append(round(min(0.99, base + monthly_step * i), 4))

    return pd.DataFrame(
        {
            "month_offset": list(range(1, months + 1)),
            "churn_probability": probs,
        }
    )


def predict_ltv_3m(
    customer_txns: pd.DataFrame,
    churn_curve: pd.DataFrame,
    fallback_aov: float,
) -> tuple[float, float]:
    """Estimate 3-month LTV from baseline monthly spend and churn survival curve."""
    if customer_txns.empty:
        baseline = max(float(fallback_aov), 0.0)
    else:
        monthly_spend = (
            customer_txns.assign(month=customer_txns["transaction_date"].dt.to_period("M").astype(str))
            .groupby("month", as_index=False)["amount"]
            .sum()
        )
        baseline = float(monthly_spend["amount"].tail(6).mean())

    expected_ltv = 0.0
    for _, row in churn_curve.iterrows():
        survival_prob = 1.0 - float(row["churn_probability"])
        expected_ltv += baseline * survival_prob

    return round(expected_ltv, 2), round(baseline, 2)


def build_customer_forecast(
    customer_txns: pd.DataFrame,
    current_probability: float,
    recency_days: float,
    fallback_aov: float,
) -> CustomerForecast:
    """Build complete 3-month churn + LTV demo forecast for one customer."""
    curve = build_churn_curve(current_probability=current_probability, recency_days=recency_days, months=3)
    predicted_ltv_3m, baseline = predict_ltv_3m(
        customer_txns=customer_txns,
        churn_curve=curve,
        fallback_aov=fallback_aov,
    )
    return CustomerForecast(
        predicted_ltv_3m=predicted_ltv_3m,
        monthly_revenue_baseline=baseline,
        churn_curve=curve,
    )
