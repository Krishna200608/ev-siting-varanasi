"""Unit tests for ML demand forecasting and explainability modules (Pipeline B).

Synopsis Stage: Stage 3 — Machine Learning Demand Modeling & SHAP.
Tests run completely offline using synthetic in-memory fixtures.
"""

from pathlib import Path
import pytest
import numpy as np
import pandas as pd

from src.ml.train_demand_model import (
    preprocess_demand_data,
    train_xgboost_regressor,
    predict_relative_demand,
)
from src.ml.explain import (
    compute_shap_values,
    generate_shap_summary_plot,
    generate_shap_artifacts,
)


@pytest.fixture
def sample_demand_data() -> tuple[pd.DataFrame, pd.Series]:
    """Fixture providing synthetic demand features and target values."""
    np.random.seed(42)
    X = pd.DataFrame(
        {
            "connection_hour": np.random.randint(0, 24, size=100),
            "day_of_week": np.random.randint(0, 7, size=100),
            "is_weekend": np.random.choice([0, 1], size=100),
            "month": np.random.randint(1, 13, size=100),
            "dwell_duration_hours": np.random.uniform(1.0, 10.0, size=100),
            "charging_duration_hours": np.random.uniform(0.5, 6.0, size=100),
        }
    )
    y = pd.Series(
        3.0 * X["charging_duration_hours"] + 0.5 * X["dwell_duration_hours"] + np.random.normal(0, 0.5, size=100),
        name="energy_kwh",
    )
    return X, y


def test_train_xgboost_regressor_cv(sample_demand_data: tuple[pd.DataFrame, pd.Series]) -> None:
    """Test that XGBoost model trains with 5-fold CV and returns positive R2 on synthetic data."""
    X, y = sample_demand_data
    model, metrics = train_xgboost_regressor(X, y, cv_folds=5, random_state=42)
    assert model is not None
    assert "r2" in metrics
    assert "rmse" in metrics
    assert "mae" in metrics
    assert "xgboost" in metrics
    assert "random_forest" in metrics
    assert "linear_regression" in metrics
    assert metrics["r2"] > 0.0


def test_predict_relative_demand_bounds(sample_demand_data: tuple[pd.DataFrame, pd.Series]) -> None:
    """Test that relative demand inference returns normalized scores bounded in [0.0, 1.0]."""
    X, y = sample_demand_data
    model, _ = train_xgboost_regressor(X, y, cv_folds=3, random_state=42)
    candidate_features = X.head(10)
    scores = predict_relative_demand(model, candidate_features)
    assert isinstance(scores, pd.Series)
    assert len(scores) == 10
    assert (scores >= 0.0).all() and (scores <= 1.0).all()


def test_compute_shap_values_dimensions(sample_demand_data: tuple[pd.DataFrame, pd.Series]) -> None:
    """Test that SHAP value output matches sample dimensions and importance table has valid structure."""
    X, y = sample_demand_data
    model, _ = train_xgboost_regressor(X, y, cv_folds=3, random_state=42)
    shap_vals, importance_df = compute_shap_values(model, X.head(20))
    assert shap_vals is not None
    assert isinstance(importance_df, pd.DataFrame)
    assert "feature" in importance_df.columns
    assert "mean_abs_shap" in importance_df.columns
    assert len(importance_df) == X.shape[1]
    assert (importance_df["mean_abs_shap"] >= 0.0).all()
