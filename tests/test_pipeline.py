"""Unit tests for segmentation/churn heuristics."""

import pandas as pd

from src.pipeline import assign_segment, churn_risk


def test_assign_segment_vip() -> None:
    row = pd.Series({"total_revenue": 30000, "frequency": 15, "recency_days": 10})
    assert assign_segment(row) == "VIP"


def test_churn_risk_high() -> None:
    row = pd.Series({"recency_days": 300})
    assert churn_risk(row) == "High"
