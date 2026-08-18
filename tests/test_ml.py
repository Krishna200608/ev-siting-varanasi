"""Unit tests for ML demand forecasting and explainability modules (Pipeline B).

Synopsis Stage: Stage 3 — Machine Learning Demand Modeling & SHAP.
Note: Tests are marked as skipped in Milestone 1 and will be enabled upon logic implementation in Milestone 4.
"""

from pathlib import Path
import pytest
import numpy as np
import pandas as pd

from src.ml.train_demand_model import preprocess_demand_data, train_xgboost_regressor, predict_relative_demand
from src.ml.explain import compute_shap_values


@pytest.fixture
def sample_demand_data() -> tuple[pd.DataFrame, pd.Series]:
    """Fixture providing synthetic demand features and target values."""
    np.random.seed(42)
    X = pd.DataFrame(
        {
            "hour": np.random.randint(0, 24, size=100),
            "day_of_week": np.random.randint(0, 7, size=100),
            "poi_count": np.random.uniform(5, 50, size=100),
            "pop_density": np.random.uniform(1000, 10000, size=100),
        }
    )
    y = pd.Series(
        2.5 * X["poi_count"] + 0.001 * X["pop_density"] + np.random.normal(0, 1, size=100),
        name="charging_demand",
    )
    return X, y


@pytest.mark.skip(reason="Milestone 4 — XGBoost training logic not yet implemented")
def test_train_xgboost_regressor_cv(sample_demand_data: tuple[pd.DataFrame, pd.Series]) -> None:
    """Test that XGBoost model trains with 5-fold CV and returns positive R2 on synthetic data."""
    X, y = sample_demand_data
    model, metrics = train_xgboost_regressor(X, y, cv_folds=5, random_state=42)
    assert model is not None
    assert "r2" in metrics
    assert "rmse" in metrics
    assert metrics["r2"] > 0.0


@pytest.mark.skip(reason="Milestone 4 — Relative demand inference logic not yet implemented")
def test_predict_relative_demand_bounds(sample_demand_data: tuple[pd.DataFrame, pd.Series]) -> None:
    """Test that relative demand inference returns normalized scores."""
    X, y = sample_demand_data
    # Placeholder model mock
    model = None
    candidate_features = X.head(10)
    scores = predict_relative_demand(model, candidate_features)
    assert isinstance(scores, pd.Series)
    assert len(scores) == 10
    assert (scores >= 0.0).all() and (scores <= 1.0).all()


@pytest.mark.skip(reason="Milestone 4 — SHAP computation logic not yet implemented")
def test_compute_shap_values_dimensions(sample_demand_data: tuple[pd.DataFrame, pd.Series]) -> None:
    """Test that SHAP value output matches sample dimensions."""
    X, _ = sample_demand_data
    model = None
    shap_vals = compute_shap_values(model, X.head(20))
    assert shap_vals is not None
