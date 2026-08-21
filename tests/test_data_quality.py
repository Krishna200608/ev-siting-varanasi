"""Unit tests for GIS Decision Matrix Data Quality and Degeneracy Safeguards.

Synopsis Stage: Stage 1 — Data Quality Validation.
All tests execute completely offline using synthetic in-memory fixtures.
"""

from pathlib import Path
import pytest
import numpy as np
import pandas as pd

from src.gis.build_decision_matrix import validate_decision_matrix_quality


@pytest.fixture
def synthetic_mixed_quality_matrix() -> pd.DataFrame:
    """Fixture containing healthy, degenerate (zero-variance), and narrow-range criteria."""
    np.random.seed(42)
    n_sites = 50
    return pd.DataFrame({
        "site_id": [f"SITE_{i:03d}" for i in range(n_sites)],
        "latitude": np.linspace(25.28, 25.34, n_sites),
        "longitude": np.linspace(82.98, 83.02, n_sites),
        # 1. Healthy criterion: wide range, high variance
        "C1_Major_Roads": np.random.uniform(2.0, 8.5, n_sites),
        # 2. Degenerate criterion: flat zero variance
        "C6_POI_Hospitals": np.ones(n_sites) * 1.0,
        # 3. Narrow-range criterion: clustered within 0.2 points
        "C6_POI_Schools": np.full(n_sites, 4.5) + np.random.uniform(-0.1, 0.1, n_sites),
        # 4. Healthy POI criterion
        "C6_POI_Shopping_Malls": np.random.uniform(1.0, 9.0, n_sites),
    })


def test_validate_decision_matrix_quality_flags_degenerate(
    synthetic_mixed_quality_matrix: pd.DataFrame
) -> None:
    """Verify that zero-variance and narrow-range columns are accurately flagged."""
    report = validate_decision_matrix_quality(
        synthetic_mixed_quality_matrix,
        min_variance_threshold=1e-4,
        min_range_threshold=0.5,
    )

    assert isinstance(report, pd.DataFrame)
    assert len(report) == 4

    # Check healthy columns
    roads_row = report[report["criterion"] == "C1_Major_Roads"].iloc[0]
    assert roads_row["status"] == "HEALTHY"
    assert roads_row["std"] > 1.0

    malls_row = report[report["criterion"] == "C6_POI_Shopping_Malls"].iloc[0]
    assert malls_row["status"] == "HEALTHY"

    # Check zero-variance column
    hosp_row = report[report["criterion"] == "C6_POI_Hospitals"].iloc[0]
    assert hosp_row["status"] == "DEGENERATE"
    assert hosp_row["std"] == 0.0
    assert "ZERO_VARIANCE" in hosp_row["issues"]

    # Check narrow-range column
    schools_row = report[report["criterion"] == "C6_POI_Schools"].iloc[0]
    assert schools_row["status"] == "WARNING"
    assert "NARROW_RANGE" in schools_row["issues"]


def test_validate_decision_matrix_quality_raises_on_degenerate(
    synthetic_mixed_quality_matrix: pd.DataFrame
) -> None:
    """Verify that raise_on_degenerate=True raises ValueError when degenerate column is present."""
    with pytest.raises(ValueError, match="Degenerate/Zero-variance criteria detected"):
        validate_decision_matrix_quality(
            synthetic_mixed_quality_matrix,
            raise_on_degenerate=True,
        )


def test_validate_decision_matrix_quality_from_clean_fixture() -> None:
    """Verify that a completely healthy decision matrix returns all HEALTHY statuses."""
    np.random.seed(42)
    n_sites = 30
    clean_df = pd.DataFrame({
        "site_id": [f"SITE_{i:03d}" for i in range(n_sites)],
        "C1_Major_Roads": np.random.uniform(1.5, 8.5, n_sites),
        "C6_POI_Schools": np.random.uniform(1.0, 9.0, n_sites),
        "C6_POI_Restaurants": np.random.uniform(2.0, 7.5, n_sites),
    })

    report = validate_decision_matrix_quality(clean_df)
    assert (report["status"] == "HEALTHY").all()
    assert (report["issues"] == "None").all()
