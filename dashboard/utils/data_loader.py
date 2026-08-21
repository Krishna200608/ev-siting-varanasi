"""Cached data loading module for EV Siting Dashboard.

Uses @st.cache_data to ensure responsive page transitions while reading
pre-computed static CSV, table, and image artifacts with zero heavy GIS/ML dependencies.
"""

from pathlib import Path
from typing import Optional
import pandas as pd
import streamlit as st

# Locate repository root relative to this file
REPO_ROOT = Path(__file__).resolve().parents[2]


def init_theme_state() -> str:
    """Initialize theme session state and return active theme ('dark' or 'light')."""
    if "theme" not in st.session_state:
        st.session_state["theme"] = "dark"
    return st.session_state["theme"]


def get_theme_colors() -> dict:
    """Return dictionary of semantic design tokens based on active theme."""
    theme = init_theme_state()
    if theme == "light":
        return {
            "theme": "light",
            "plotly_template": "plotly_white",
            "folium_tiles": "CartoDB positron",
            "bg_color": "#f8fafc",
            "card_bg": "#ffffff",
            "text_color": "#0f172a",
            "secondary_text": "#475569",
            "border_color": "#e2e8f0",
            "highlight_green": "#16a34a",
            "highlight_blue": "#2563eb",
            "highlight_red": "#dc2626",
            "healthy_bg": "#dcfce7",
            "healthy_text": "#166534",
            "degenerate_bg": "#fee2e2",
            "degenerate_text": "#991b1b",
        }
    else:
        return {
            "theme": "dark",
            "plotly_template": "plotly_dark",
            "folium_tiles": "CartoDB dark_matter",
            "bg_color": "#0e1117",
            "card_bg": "#1e222d",
            "text_color": "#f1f5f9",
            "secondary_text": "#94a3b8",
            "border_color": "#334155",
            "highlight_green": "#22c55e",
            "highlight_blue": "#3b82f6",
            "highlight_red": "#ef4444",
            "healthy_bg": "#064e3b",
            "healthy_text": "#6ee7b7",
            "degenerate_bg": "#7f1d1d",
            "degenerate_text": "#fca5a5",
        }


def apply_custom_theme() -> None:
    """Inject dynamic CSS into the page matching active theme tokens."""
    colors = get_theme_colors()
    if colors["theme"] == "light":
        css = """
        <style>
        /* Light Mode Custom Styling */
        .stApp {
            background-color: #f8fafc;
            color: #0f172a;
        }
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e2e8f0;
        }
        [data-testid="stMetricValue"] {
            color: #0f172a !important;
        }
        [data-testid="stMetricLabel"] {
            color: #475569 !important;
        }
        </style>
        """
    else:
        css = """
        <style>
        /* Dark Mode Custom Styling */
        .stApp {
            background-color: #0e1117;
            color: #f1f5f9;
        }
        [data-testid="stSidebar"] {
            background-color: #161a24;
            border-right: 1px solid #2e3440;
        }
        [data-testid="stMetricValue"] {
            color: #f1f5f9 !important;
        }
        [data-testid="stMetricLabel"] {
            color: #94a3b8 !important;
        }
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)


def render_theme_toggle() -> str:
    """Render an interactive theme toggle in the sidebar with dynamic icon and label."""
    theme = init_theme_state()
    
    if theme == "dark":
        if st.sidebar.button(
            "Switch to Light Mode",
            icon=":material/light_mode:",
            help="Switch dashboard appearance to Light Mode",
            use_container_width=True,
            key="theme_toggle_btn",
        ):
            st.session_state["theme"] = "light"
            st.rerun()
    else:
        if st.sidebar.button(
            "Switch to Dark Mode",
            icon=":material/dark_mode:",
            help="Switch dashboard appearance to Dark Mode",
            use_container_width=True,
            key="theme_toggle_btn",
        ):
            st.session_state["theme"] = "dark"
            st.rerun()

    return st.session_state["theme"]


def render_sidebar_logo() -> None:
    """Render the official project logo and theme toggle in the sidebar."""
    apply_custom_theme()
    logo_path = REPO_ROOT / "assets" / "Logos" / "Logo_1.png"
    if logo_path.exists():
        st.sidebar.image(str(logo_path), use_container_width=True)
    
    render_theme_toggle()
    st.sidebar.markdown("---")



@st.cache_data
def load_decision_matrix(version: str = "v2") -> pd.DataFrame:
    """Load the processed GIS decision matrix (v1 baseline or v2 equal-scrutiny)."""
    if version == "v1":
        file_path = REPO_ROOT / "data" / "processed" / "gis" / "decision_matrix_full.csv"
    else:
        file_path = REPO_ROOT / "data" / "processed" / "gis" / "decision_matrix_full_v2.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"Decision matrix file not found at: {file_path}")
    return pd.read_csv(file_path)


@st.cache_data
def load_mcdm_rankings(version: str = "v2") -> pd.DataFrame:
    """Load consolidated multi-criteria decision making rankings."""
    if version == "v1":
        file_path = REPO_ROOT / "outputs" / "tables" / "mcdm_rankings_full.csv"
    else:
        file_path = REPO_ROOT / "outputs" / "tables" / "mcdm_rankings_full_v2.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"MCDM rankings table not found at: {file_path}")
    return pd.read_csv(file_path)


@st.cache_data
def load_sensitivity_results(mode: str = "full_v2") -> pd.DataFrame:
    """Load 12-scenario sensitivity analysis results table."""
    if mode == "sample":
        file_path = REPO_ROOT / "outputs" / "tables" / "mcdm_sensitivity_results.csv"
    elif mode == "full_v1":
        file_path = REPO_ROOT / "outputs" / "tables" / "mcdm_sensitivity_results_full.csv"
    else:
        file_path = REPO_ROOT / "outputs" / "tables" / "mcdm_sensitivity_results_full_v2.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"Sensitivity results file not found at: {file_path}")
    return pd.read_csv(file_path)


@st.cache_data
def load_temporal_curve() -> pd.DataFrame:
    """Load 24-hour diurnal load profile table (weekday vs weekend)."""
    file_path = REPO_ROOT / "outputs" / "tables" / "temporal_demand_curve.csv"
    if not file_path.exists():
        raise FileNotFoundError(f"Temporal curve table not found at: {file_path}")
    return pd.read_csv(file_path)


@st.cache_data
def load_data_quality_audit_table() -> pd.DataFrame:
    """Load or assemble the systematic 9-criteria x 2-version data-quality audit table."""
    v1_df = load_decision_matrix("v1")
    v2_df = load_decision_matrix("v2")

    criteria_cols = [c for c in v1_df.columns if c not in ["site_id", "latitude", "longitude"]]
    raw_counts_v1 = {
        "C1_Major_Roads": 579,
        "C5_Competitor_EVCS": 0,
        "C6_POI_Schools": 452,
        "C6_POI_Shopping_Malls": 325,
        "C6_POI_Restaurants": 238,
        "C6_POI_Hospitals": 20,
        "C6_POI_Theatres": 10,
        "C6_POI_Bus_Stops": 11,
        "C6_POI_Petrol_Bunks": 20,
    }
    raw_counts_v2 = {
        "C1_Major_Roads": 579,
        "C5_Competitor_EVCS": 0,
        "C6_POI_Schools": 511,
        "C6_POI_Shopping_Malls": 587,
        "C6_POI_Restaurants": 378,
        "C6_POI_Hospitals": 280,
        "C6_POI_Theatres": 13,
        "C6_POI_Bus_Stops": 11,
        "C6_POI_Petrol_Bunks": 22,
    }

    records = []
    for col in criteria_cols:
        s1 = v1_df[col]
        s2 = v2_df[col]
        
        status_v1 = "DEGENERATE" if (s1.std() == 0.0) else "HEALTHY"
        status_v2 = "DEGENERATE" if (s2.std() == 0.0) else "HEALTHY"
        
        records.append({
            "Criterion": col,
            "v1 Raw POIs": raw_counts_v1.get(col, 0),
            "v1 Min": round(float(s1.min()), 4),
            "v1 Max": round(float(s1.max()), 4),
            "v1 Mean": round(float(s1.mean()), 4),
            "v1 Std Dev": round(float(s1.std()), 4),
            "v1 Range (Δ)": round(float(s1.max() - s1.min()), 4),
            "v1 Status": status_v1,
            "v2 Raw POIs": raw_counts_v2.get(col, 0),
            "v2 Min": round(float(s2.min()), 4),
            "v2 Max": round(float(s2.max()), 4),
            "v2 Mean": round(float(s2.mean()), 4),
            "v2 Std Dev": round(float(s2.std()), 4),
            "v2 Range (Δ)": round(float(s2.max() - s2.min()), 4),
            "v2 Status": status_v2,
        })
    return pd.DataFrame(records)


def get_figure_path(figure_filename: str) -> Path:
    """Retrieve absolute Path to a static pre-generated figure."""
    path = REPO_ROOT / "outputs" / "figures" / figure_filename
    if not path.exists():
        raise FileNotFoundError(f"Figure file not found: {path}")
    return path
