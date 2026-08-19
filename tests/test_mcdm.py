"""Unit tests for MCDM weighting and ranking modules (Pipeline A).

Synopsis Stage: Stage 2 — Multi-Criteria Decision Analysis.
Theoretical Foundation: Rashmitha, Sushma & Roy (2024); Guo & Zhao (2015).
"""

from pathlib import Path
import pytest
import numpy as np
import pandas as pd

from src.mcdm.weighting import compute_critic_weights, compute_entropy_weights
from src.mcdm.ranking import compute_topsis_ranking, compute_waspas_ranking
from src.mcdm.pipeline import run_mcdm_pipeline


@pytest.fixture
def sample_decision_matrix() -> pd.DataFrame:
    """Fixture providing a minimal 4-alternative x 3-criteria decision matrix."""
    return pd.DataFrame(
        {
            "C1_Traffic": [100.0, 150.0, 80.0, 200.0],
            "C2_Population": [5000.0, 8000.0, 3000.0, 10000.0],
            "C3_LandCost": [2500.0, 4000.0, 1500.0, 5000.0],
        },
        index=["Site_A", "Site_B", "Site_C", "Site_D"],
    )


# ---------------------------------------------------------------------------
# 1. Weighting Algorithm Tests
# ---------------------------------------------------------------------------

def test_compute_critic_weights_shape_and_sum(sample_decision_matrix: pd.DataFrame) -> None:
    """Test that CRITIC weights sum to 1.0 and match criteria dimensions."""
    criteria_types = ["benefit", "benefit", "cost"]
    weights = compute_critic_weights(sample_decision_matrix, criteria_types)
    assert isinstance(weights, np.ndarray)
    assert len(weights) == 3
    assert np.isclose(weights.sum(), 1.0)
    assert (weights >= 0.0).all()


def test_compute_entropy_weights_shape_and_sum(sample_decision_matrix: pd.DataFrame) -> None:
    """Test that Entropy weights sum to 1.0 and match criteria dimensions."""
    criteria_types = ["benefit", "benefit", "cost"]
    weights = compute_entropy_weights(sample_decision_matrix, criteria_types)
    assert isinstance(weights, np.ndarray)
    assert len(weights) == 3
    assert np.isclose(weights.sum(), 1.0)
    assert (weights >= 0.0).all()


def test_zero_variance_criterion_handling() -> None:
    """Test that CRITIC and Entropy handle zero-variance criteria without division-by-zero or NaNs."""
    df_constant = pd.DataFrame(
        {
            "C1_Varying": [1.0, 5.0, 9.0],
            "C2_Constant": [5.0, 5.0, 5.0],
            "C3_Varying": [10.0, 20.0, 30.0],
        }
    )
    criteria_types = ["benefit", "benefit", "benefit"]

    critic_w = compute_critic_weights(df_constant, criteria_types)
    assert isinstance(critic_w, np.ndarray)
    assert len(critic_w) == 3
    assert not np.isnan(critic_w).any()
    assert np.isclose(critic_w.sum(), 1.0)
    # The constant criterion has 0 contrast intensity, so its CRITIC weight should be 0
    assert np.isclose(critic_w[1], 0.0)

    entropy_w = compute_entropy_weights(df_constant, criteria_types)
    assert isinstance(entropy_w, np.ndarray)
    assert len(entropy_w) == 3
    assert not np.isnan(entropy_w).any()
    assert np.isclose(entropy_w.sum(), 1.0)


# ---------------------------------------------------------------------------
# 2. Ranking Algorithm Tests
# ---------------------------------------------------------------------------

def test_compute_topsis_ranking_structure(sample_decision_matrix: pd.DataFrame) -> None:
    """Test that TOPSIS ranking returns proper columns and valid closeness coefficients."""
    weights = np.array([0.4, 0.4, 0.2])
    criteria_types = ["benefit", "benefit", "cost"]
    results = compute_topsis_ranking(sample_decision_matrix, weights, criteria_types)
    assert isinstance(results, pd.DataFrame)
    assert "closeness_coefficient" in results.columns
    assert "rank" in results.columns
    assert len(results) == 4
    assert (results["closeness_coefficient"] >= 0.0).all()
    assert (results["closeness_coefficient"] <= 1.0).all()
    # Ranks must be a permutation of 1 to 4
    assert sorted(results["rank"].values) == [1, 2, 3, 4]


def test_compute_waspas_ranking_structure(sample_decision_matrix: pd.DataFrame) -> None:
    """Test that WASPAS ranking returns proper columns and score bounds."""
    weights = np.array([0.4, 0.4, 0.2])
    criteria_types = ["benefit", "benefit", "cost"]
    results = compute_waspas_ranking(sample_decision_matrix, weights, criteria_types)
    assert isinstance(results, pd.DataFrame)
    assert "waspas_score" in results.columns
    assert "rank" in results.columns
    assert len(results) == 4
    assert (results["waspas_score"] >= 0.0).all()
    assert (results["waspas_score"] <= 1.0).all()
    assert sorted(results["rank"].values) == [1, 2, 3, 4]


def test_cost_criterion_inversion() -> None:
    """Test that higher values on a cost criterion properly penalize site ranking."""
    # Site 1 has lower cost than Site 2 with identical benefit
    df = pd.DataFrame(
        {
            "Benefit_POI": [8.0, 8.0],
            "Cost_Competition": [2.0, 9.0],  # Site 1 has low competition, Site 2 has high competition
        },
        index=["Site_LowComp", "Site_HighComp"],
    )
    weights = np.array([0.5, 0.5])
    criteria_types = ["benefit", "cost"]

    topsis_res = compute_topsis_ranking(df, weights, criteria_types)
    assert topsis_res.loc["Site_LowComp", "rank"] == 1
    assert topsis_res.loc["Site_HighComp", "rank"] == 2
    assert topsis_res.loc["Site_LowComp", "closeness_coefficient"] > topsis_res.loc["Site_HighComp", "closeness_coefficient"]

    waspas_res = compute_waspas_ranking(df, weights, criteria_types)
    assert waspas_res.loc["Site_LowComp", "rank"] == 1
    assert waspas_res.loc["Site_HighComp", "rank"] == 2


# ---------------------------------------------------------------------------
# 3. End-to-End Pipeline Integration Test
# ---------------------------------------------------------------------------

def test_run_mcdm_pipeline_integration(tmp_path: Path) -> None:
    """Test end-to-end execution of the MCDM pipeline against processed GIS decision matrix."""
    real_matrix_path = Path("data/processed/gis/decision_matrix.csv")
    if not real_matrix_path.exists():
        pytest.skip("decision_matrix.csv not found; skipping integration test.")

    out_csv = tmp_path / "test_rankings.csv"
    rankings_df = run_mcdm_pipeline(
        decision_matrix_path=real_matrix_path,
        config_path=Path("config/criteria.yaml"),
        output_table_path=out_csv,
    )

    assert isinstance(rankings_df, pd.DataFrame)
    assert len(rankings_df) == 30
    assert "topsis_critic_score" in rankings_df.columns
    assert "topsis_critic_rank" in rankings_df.columns
    assert "topsis_entropy_score" in rankings_df.columns
    assert "topsis_entropy_rank" in rankings_df.columns
    assert "waspas_critic_score" in rankings_df.columns
    assert "waspas_critic_rank" in rankings_df.columns
    assert "waspas_entropy_score" in rankings_df.columns
    assert "waspas_entropy_rank" in rankings_df.columns

    # Verify no NaN values in scores or ranks
    assert not rankings_df.isna().any().any()
    assert out_csv.exists()
