"""Unit tests for Stage 4 integration, temporal demand profiling, and sensitivity analysis.

Synopsis Stage: Stage 4 — Two-Stage Integration & Robustness.
All tests execute completely offline using synthetic in-memory fixtures.
"""

from pathlib import Path
import pytest
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin

from src.integration.temporal_curve import generate_temporal_demand_profile
from src.integration.sensitivity_analysis import (
    run_mcdm_criteria_sensitivity,
    generate_mcdm_sensitivity_figure,
)


class MockTemporalModel(BaseEstimator, RegressorMixin):
    """Mock regression model for testing diurnal temporal curve generator."""

    def fit(self, X: pd.DataFrame, y: np.ndarray) -> "MockTemporalModel":
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        # Synthetic diurnal curve peaking around hour 14
        hours = X["connection_hour"].to_numpy()
        return 10.0 + 3.0 * np.sin(np.pi * (hours - 6) / 12.0)


@pytest.fixture
def synthetic_decision_matrix() -> tuple[pd.DataFrame, list[str]]:
    """Fixture providing synthetic decision matrix and criteria types."""
    np.random.seed(42)
    n_sites = 20
    criteria_types = ["benefit", "cost", "benefit", "benefit", "benefit", "benefit", "benefit", "benefit", "benefit"]
    
    data = {
        "site_id": [f"SITE_{i+1:03d}" for i in range(n_sites)],
        "C1_Major_Roads": np.random.uniform(5.0, 10.0, size=n_sites),
        "C5_Competitor_EVCS": np.random.uniform(0.5, 3.0, size=n_sites),
        "C6_POI_Schools": np.random.uniform(1.0, 8.0, size=n_sites),
        "C6_POI_Shopping_Malls": np.random.uniform(0.0, 6.0, size=n_sites),
        "C6_POI_Restaurants": np.random.uniform(2.0, 9.0, size=n_sites),
        "C6_POI_Hospitals": np.random.uniform(0.5, 5.0, size=n_sites),
        "C6_POI_Theatres": np.random.uniform(0.0, 4.0, size=n_sites),
        "C6_POI_Bus_Stops": np.random.uniform(1.0, 7.0, size=n_sites),
        "C6_POI_Petrol_Bunks": np.random.uniform(0.5, 5.0, size=n_sites),
    }
    df = pd.DataFrame(data)
    return df, criteria_types


def test_generate_temporal_demand_profile_mock(tmp_path: Path) -> None:
    """Test that diurnal temporal demand profile generates 24 hourly rows and positive kWh values."""
    mock_model = MockTemporalModel()
    table_path = tmp_path / "temporal_curve.csv"
    fig_path = tmp_path / "temporal_curve.png"

    df = generate_temporal_demand_profile(
        model=mock_model,
        output_table_path=table_path,
        output_figure_path=fig_path,
    )

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 24
    assert list(df.columns) == ["hour", "weekday_kwh", "weekend_kwh", "weighted_avg_kwh"]
    assert (df["hour"] == np.arange(24)).all()
    assert (df["weekday_kwh"] >= 0.0).all()
    assert (df["weekend_kwh"] >= 0.0).all()
    assert (df["weighted_avg_kwh"] >= 0.0).all()
    assert table_path.exists()
    assert fig_path.exists()


def test_run_mcdm_criteria_sensitivity_structure(
    synthetic_decision_matrix: tuple[pd.DataFrame, list[str]], tmp_path: Path
) -> None:
    """Test that 12-scenario sensitivity analysis executes and returns valid metrics."""
    dec_df, criteria_types = synthetic_decision_matrix
    criteria_cols = [c for c in dec_df.columns if c != "site_id"]
    output_csv = tmp_path / "mcdm_sensitivity.csv"

    sens_df = run_mcdm_criteria_sensitivity(
        decision_matrix=dec_df[criteria_cols],
        criteria_types=criteria_types,
        perturbation_pct=0.20,
        top_n=5,
        output_table_path=output_csv,
    )

    assert isinstance(sens_df, pd.DataFrame)
    # 9 individual + 1 equal + 1 road + 1 mall = 12 scenarios
    assert len(sens_df) == 12
    assert "scenario_id" in sens_df.columns
    assert "spearman_rho" in sens_df.columns
    assert "kendall_tau" in sens_df.columns
    assert "top5_overlap_pct" in sens_df.columns
    assert "max_rank_shift" in sens_df.columns

    # Check bounds
    assert (sens_df["spearman_rho"] >= -1.0).all() and (sens_df["spearman_rho"] <= 1.0).all()
    assert (sens_df["kendall_tau"] >= -1.0).all() and (sens_df["kendall_tau"] <= 1.0).all()
    assert (sens_df["top5_overlap_pct"] >= 0.0).all() and (sens_df["top5_overlap_pct"] <= 100.0).all()
    assert output_csv.exists()


def test_generate_mcdm_sensitivity_figure(
    synthetic_decision_matrix: tuple[pd.DataFrame, list[str]], tmp_path: Path
) -> None:
    """Test that sensitivity visualization renders successfully."""
    dec_df, criteria_types = synthetic_decision_matrix
    criteria_cols = [c for c in dec_df.columns if c != "site_id"]
    sens_df = run_mcdm_criteria_sensitivity(
        decision_matrix=dec_df[criteria_cols],
        criteria_types=criteria_types,
        perturbation_pct=0.20,
        top_n=5,
        output_table_path=None,
    )

    fig_path = tmp_path / "sensitivity_plot.png"
    generate_mcdm_sensitivity_figure(sens_df, output_figure_path=fig_path)
    assert fig_path.exists()
    assert fig_path.stat().st_size > 1000
