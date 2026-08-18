"""Unit tests for MCDM weighting and ranking modules (Pipeline A).

Synopsis Stage: Stage 2 — Multi-Criteria Decision Analysis.
Note: Tests are marked as skipped in Milestone 1 and will be enabled upon logic implementation in Milestone 3.
"""

import pytest
import numpy as np
import pandas as pd

from src.mcdm.weighting import compute_critic_weights, compute_entropy_weights
from src.mcdm.ranking import compute_topsis_ranking, compute_waspas_ranking


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


@pytest.mark.skip(reason="Milestone 3 — CRITIC weighting logic not yet implemented")
def test_compute_critic_weights_shape_and_sum(sample_decision_matrix: pd.DataFrame) -> None:
    """Test that CRITIC weights sum to 1.0 and match criteria dimensions."""
    criteria_types = ["benefit", "benefit", "cost"]
    weights = compute_critic_weights(sample_decision_matrix, criteria_types)
    assert isinstance(weights, np.ndarray)
    assert len(weights) == 3
    assert np.isclose(weights.sum(), 1.0)


@pytest.mark.skip(reason="Milestone 3 — Entropy weighting logic not yet implemented")
def test_compute_entropy_weights_shape_and_sum(sample_decision_matrix: pd.DataFrame) -> None:
    """Test that Entropy weights sum to 1.0 and match criteria dimensions."""
    criteria_types = ["benefit", "benefit", "cost"]
    weights = compute_entropy_weights(sample_decision_matrix, criteria_types)
    assert isinstance(weights, np.ndarray)
    assert len(weights) == 3
    assert np.isclose(weights.sum(), 1.0)


@pytest.mark.skip(reason="Milestone 3 — TOPSIS ranking logic not yet implemented")
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


@pytest.mark.skip(reason="Milestone 3 — WASPAS ranking logic not yet implemented")
def test_compute_waspas_ranking_structure(sample_decision_matrix: pd.DataFrame) -> None:
    """Test that WASPAS ranking returns proper columns and score bounds."""
    weights = np.array([0.4, 0.4, 0.2])
    criteria_types = ["benefit", "benefit", "cost"]
    results = compute_waspas_ranking(sample_decision_matrix, weights, criteria_types)
    assert isinstance(results, pd.DataFrame)
    assert "waspas_score" in results.columns
    assert "rank" in results.columns
    assert len(results) == 4
