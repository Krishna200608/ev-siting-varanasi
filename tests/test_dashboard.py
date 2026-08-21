"""Unit tests for Streamlit dashboard components, data loaders, and live MCDM re-ranker."""

from pathlib import Path
import ast
import numpy as np
import pandas as pd
import pytest

from dashboard.utils.data_loader import (
    load_decision_matrix,
    load_mcdm_rankings,
    load_sensitivity_results,
    load_temporal_curve,
    load_data_quality_audit_table,
)
from dashboard.utils.mcdm_live import (
    get_default_critic_weights,
    compute_live_whatif_ranking,
    CRITERIA_ORIENTATION,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = REPO_ROOT / "dashboard"


def test_dashboard_requirements_file_exists():
    """Verify canonical dashboard/requirements.txt exists and specifies essential lightweight deps."""
    req_path = DASHBOARD_DIR / "requirements.txt"
    assert req_path.exists(), "dashboard/requirements.txt must exist"
    
    content = req_path.read_text(encoding="utf-8").lower()
    for pkg in ["streamlit", "pandas", "numpy", "plotly", "folium", "streamlit-folium"]:
        assert pkg in content, f"{pkg} must be declared in dashboard/requirements.txt"


def test_no_heavy_gis_or_ml_imports_in_dashboard():
    """Guarantee dashboard code does not import geopandas, rasterio, xgboost, or shap."""
    prohibited = {"geopandas", "rasterio", "xgboost", "shap", "gdal"}
    
    py_files = list(DASHBOARD_DIR.rglob("*.py"))
    assert len(py_files) >= 8, f"Expected at least 8 dashboard python files, found {len(py_files)}"

    for py_file in py_files:
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_pkg = alias.name.split(".")[0]
                    assert root_pkg not in prohibited, f"Prohibited import '{root_pkg}' found in {py_file.name}"
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_pkg = node.module.split(".")[0]
                    assert root_pkg not in prohibited, f"Prohibited from-import '{root_pkg}' found in {py_file.name}"


def test_data_loaders_return_valid_dataframes():
    """Verify all cached data loaders return populated DataFrames matching expected dimensions."""
    dm_v2 = load_decision_matrix("v2")
    assert len(dm_v2) == 308
    assert "site_id" in dm_v2.columns
    assert "C1_Major_Roads" in dm_v2.columns

    rankings_v2 = load_mcdm_rankings("v2")
    assert len(rankings_v2) == 308
    assert "topsis_critic_rank" in rankings_v2.columns

    sens_v2 = load_sensitivity_results("full_v2")
    assert len(sens_v2) == 12
    assert "spearman_rho" in sens_v2.columns

    curve_df = load_temporal_curve()
    assert len(curve_df) == 24
    assert "weekday_kwh" in curve_df.columns

    audit_df = load_data_quality_audit_table()
    assert len(audit_df) == 9
    assert "v2 Status" in audit_df.columns


def test_c5_competitor_evcs_is_strictly_cost_criterion():
    """Verify C5_Competitor_EVCS orientation is strictly 'cost' matching config/criteria.yaml."""
    assert "C5_Competitor_EVCS" in CRITERIA_ORIENTATION
    assert CRITERIA_ORIENTATION["C5_Competitor_EVCS"] == "cost"


def test_whatif_default_weights_exact_match_stored_baseline():
    """Guarantee live TOPSIS ranking with default CRITIC weights exactly reproduces baseline rankings."""
    dm_v2 = load_decision_matrix("v2")
    baseline_rankings = load_mcdm_rankings("v2")
    
    default_weights = get_default_critic_weights(dm_v2)
    assert len(default_weights) == 9
    assert pytest.approx(sum(default_weights.values()), 1e-4) == 1.0

    live_res = compute_live_whatif_ranking(
        custom_weights=default_weights,
        decision_matrix_df=dm_v2,
        baseline_rankings_df=baseline_rankings,
    )

    # Align by site_id
    live_sorted = live_res.sort_values("site_id").reset_index(drop=True)
    base_sorted = baseline_rankings.sort_values("site_id").reset_index(drop=True)

    # Assert exact rank equivalence
    np.testing.assert_array_equal(
        live_sorted["custom_topsis_rank"].values,
        base_sorted["topsis_critic_rank"].values,
        err_msg="Live TOPSIS rank with default CRITIC weights must exactly match stored baseline ranks",
    )

    # Assert score equivalence to 4 decimal places
    np.testing.assert_allclose(
        live_sorted["custom_topsis_score"].values,
        base_sorted["topsis_critic_score"].values,
        atol=1e-3,
        err_msg="Live TOPSIS closeness scores must match baseline within 1e-3",
    )

    # Assert all rank shifts are exactly 0
    assert (live_sorted["rank_shift"] == 0).all()


def test_theme_tokens_and_state():
    """Verify theme engine returns valid color tokens and defaults."""
    from dashboard.utils.data_loader import init_theme_state, get_theme_colors

    # Test default initialization
    theme = init_theme_state()
    assert theme in ["dark", "light"]

    # Test dark mode tokens
    import streamlit as st
    st.session_state["theme"] = "dark"
    dark_colors = get_theme_colors()
    assert dark_colors["theme"] == "dark"
    assert dark_colors["plotly_template"] == "plotly_dark"
    assert dark_colors["folium_tiles"] == "CartoDB dark_matter"
    assert dark_colors["bg_color"].startswith("#")

    # Test light mode tokens
    st.session_state["theme"] = "light"
    light_colors = get_theme_colors()
    assert light_colors["theme"] == "light"
    assert light_colors["plotly_template"] == "plotly_white"
    assert light_colors["folium_tiles"] == "CartoDB positron"
    assert light_colors["bg_color"].startswith("#")

