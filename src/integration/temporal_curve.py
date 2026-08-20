"""Pipeline B: ML Demand Forecasting — Standalone Diurnal Temporal Curve Generator.

Synopsis Stage: Stage 3 / Stage 4 — Operational Demand Profiling.
Theoretical Foundation: Zhang, Peng & Zeng (2025, Sustainability); Lee, Li & Low (2019, ACM e-Energy).

This module evaluates the transferability-constrained XGBoost demand model over a synthetic 24-hour
diurnal cycle across representative weekdays and weekends. It establishes when charging energy demand peaks
city-wide to inform operational scheduling, dynamic tariff design, and grid load balancing.
"""

import pickle
from pathlib import Path
from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def generate_temporal_demand_profile(
    model: Optional[Any] = None,
    model_path: Path = Path("outputs/models/demand_xgboost_transferable.pkl"),
    output_table_path: Path = Path("outputs/tables/temporal_demand_curve.csv"),
    output_figure_path: Path = Path("outputs/figures/temporal_demand_curve.png"),
    representative_month: int = 5,
) -> pd.DataFrame:
    """Evaluate 24-hour diurnal charging demand for representative weekday and weekend days.

    Args:
        model: Pre-loaded model object (or None to load from model_path).
        model_path: Path to pickled transferable XGBoost model.
        output_table_path: Destination path for output CSV table.
        output_figure_path: Destination path for rendered PNG plot.
        representative_month: Month integer for seasonal baseline (default: 5, May).

    Returns:
        DataFrame with columns [hour, weekday_kwh, weekend_kwh, weighted_avg_kwh].
    """
    output_table_path = Path(output_table_path)
    output_figure_path = Path(output_figure_path)

    output_table_path.parent.mkdir(parents=True, exist_ok=True)
    output_figure_path.parent.mkdir(parents=True, exist_ok=True)

    if model is None:
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Transferable demand model not found at {model_path}")
        with open(model_path, "rb") as f:
            model = pickle.load(f)

    hours = list(range(24))

    # Representative Weekday: Wednesday (day_of_week=2, is_weekend=0)
    weekday_df = pd.DataFrame(
        {
            "connection_hour": hours,
            "day_of_week": 2,
            "is_weekend": 0,
            "month": representative_month,
        }
    )

    # Representative Weekend: Saturday (day_of_week=5, is_weekend=1)
    weekend_df = pd.DataFrame(
        {
            "connection_hour": hours,
            "day_of_week": 5,
            "is_weekend": 1,
            "month": representative_month,
        }
    )

    pred_weekday = model.predict(weekday_df)
    pred_weekend = model.predict(weekend_df)

    pred_weekday = np.maximum(0.0, np.nan_to_num(pred_weekday, nan=0.0))
    pred_weekend = np.maximum(0.0, np.nan_to_num(pred_weekend, nan=0.0))

    # Weighted 7-day average: (5 * weekday + 2 * weekend) / 7
    weighted_avg = (5.0 * pred_weekday + 2.0 * pred_weekend) / 7.0

    profile_df = pd.DataFrame(
        {
            "hour": hours,
            "weekday_kwh": [round(float(v), 4) for v in pred_weekday],
            "weekend_kwh": [round(float(v), 4) for v in pred_weekend],
            "weighted_avg_kwh": [round(float(v), 4) for v in weighted_avg],
        }
    )

    profile_df.to_csv(output_table_path, index=False)

    # Render publication-grade figure
    plt.figure(figsize=(10, 5.5))
    plt.plot(profile_df["hour"], profile_df["weekday_kwh"], label="Weekday (Mon–Fri)", color="#1f77b4", linewidth=2.5, marker="o", markersize=4)
    plt.plot(profile_df["hour"], profile_df["weekend_kwh"], label="Weekend (Sat–Sun)", color="#ff7f0e", linewidth=2.5, linestyle="--", marker="s", markersize=4)
    plt.plot(profile_df["hour"], profile_df["weighted_avg_kwh"], label="7-Day Weighted Mean", color="#2ca02c", linewidth=2.0, linestyle=":", alpha=0.85)

    plt.title("Diurnal EV Charging Demand Profile (ACN-Data Transferable Model)", fontsize=13, pad=12, fontweight="bold")
    plt.xlabel("Connection Arrival Hour (00:00 – 23:00)", fontsize=11)
    plt.ylabel("Predicted Energy Demand per Session (kWh)", fontsize=11)
    plt.xticks(hours)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(frameon=True, facecolor="white", edgecolor="none")
    plt.tight_layout()
    plt.savefig(output_figure_path, dpi=300, bbox_inches="tight")
    plt.close()

    return profile_df


if __name__ == "__main__":
    generate_temporal_demand_profile()
