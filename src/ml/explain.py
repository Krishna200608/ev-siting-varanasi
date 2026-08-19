"""Pipeline B: ML Demand Forecasting — SHAP Model Interpretability.

Synopsis Stage: Stage 3 — Explainable AI via SHapley Additive exPlanations (SHAP).
Theoretical Foundation: Zhang, Peng & Zeng (2025, Sustainability); Lundberg & Lee (2017, NeurIPS).

This module applies SHAP (cooperative game-theoretic feature attribution) to explain
the XGBoost demand forecasting model:
1. Global Interpretability: Identifies key demand-driving features across the training domain.
2. Local Interpretability: Deconstructs predictions for individual candidate site profiles,
   validating whether the transferred relationships align with urban mobility logic.
"""

from pathlib import Path
from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap


def compute_shap_values(
    model: Any,
    X_sample: pd.DataFrame,
) -> tuple[Any, pd.DataFrame]:
    """Calculate SHAP values for the fitted tree ensemble model and compute mean absolute importance.

    Args:
        model: Fitted XGBoost model object (or None for testing stub).
        X_sample: Sample DataFrame of input features to explain.

    Returns:
        Tuple of (SHAP Explanation/values object, ranked feature importance DataFrame).
    """
    if model is None:
        # Mock SHAP values for unit testing
        n_samples, n_features = X_sample.shape
        mock_values = np.random.uniform(0.1, 1.0, size=(n_samples, n_features))
        importance_df = pd.DataFrame(
            {
                "feature": X_sample.columns,
                "mean_abs_shap": np.mean(np.abs(mock_values), axis=0),
            }
        ).sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)
        return mock_values, importance_df

    explainer = shap.TreeExplainer(model)
    shap_values = explainer(X_sample)

    # Extract numeric values
    if hasattr(shap_values, "values"):
        vals = shap_values.values
    else:
        vals = np.array(shap_values)

    mean_abs_shap = np.mean(np.abs(vals), axis=0)

    importance_df = pd.DataFrame(
        {
            "feature": list(X_sample.columns),
            "mean_abs_shap": [round(float(v), 4) for v in mean_abs_shap],
        }
    ).sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)

    return shap_values, importance_df


def generate_shap_summary_plot(
    shap_values: Any,
    X_sample: pd.DataFrame,
    output_figure_path: Path,
) -> None:
    """Generate and save SHAP beeswarm / summary plot illustrating feature impact and directionality.

    Args:
        shap_values: Computed SHAP Explanation object.
        X_sample: Feature matrix corresponding to shap_values.
        output_figure_path: Destination file path for the output figure.
    """
    output_figure_path = Path(output_figure_path)
    output_figure_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(9, 6))
    if hasattr(shap_values, "values"):
        shap.summary_plot(shap_values.values, X_sample, show=False)
    else:
        shap.summary_plot(shap_values, X_sample, show=False)

    plt.title("SHAP Global Feature Importance (ACN-Data Demand Regressor)", fontsize=12, pad=15)
    plt.tight_layout()
    plt.savefig(output_figure_path, dpi=300, bbox_inches="tight")
    plt.close()


def generate_shap_artifacts(
    model: Any,
    X_sample: pd.DataFrame,
    figure_output_path: Path = Path("outputs/figures/shap_summary.png"),
    table_output_path: Path = Path("outputs/tables/shap_feature_importance.csv"),
) -> tuple[Any, pd.DataFrame]:
    """Orchestrate SHAP attribution calculation, summary plot rendering, and table export.

    Args:
        model: Fitted XGBoost regressor model.
        X_sample: Feature matrix used for attribution.
        figure_output_path: Output PNG figure path.
        table_output_path: Output CSV table path.

    Returns:
        Tuple of (computed shap_values object, ranked importance DataFrame).
    """
    figure_output_path = Path(figure_output_path)
    table_output_path = Path(table_output_path)

    figure_output_path.parent.mkdir(parents=True, exist_ok=True)
    table_output_path.parent.mkdir(parents=True, exist_ok=True)

    shap_values, importance_df = compute_shap_values(model, X_sample)
    importance_df.to_csv(table_output_path, index=False)
    generate_shap_summary_plot(shap_values, X_sample, figure_output_path)

    return shap_values, importance_df
