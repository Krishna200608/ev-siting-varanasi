"""Page 5: Multi-Scenario Sensitivity Analysis & Scale-Dependent Dynamics."""

import sys
from pathlib import Path
from PIL import Image
import pandas as pd
import plotly.express as px
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.utils.data_loader import load_sensitivity_results, get_figure_path, render_sidebar_logo
from dashboard.utils.theming import inject_theme_and_toggle, apply_plotly_theme


st.set_page_config(page_title="Sensitivity Analysis — EV Siting Varanasi", page_icon=":material/query_stats:", layout="wide")
inject_theme_and_toggle()
render_sidebar_logo()

st.title(":material/query_stats: Multi-Scenario Sensitivity & Scale-Dependent Dynamics")
st.markdown(
    "Following Rashmitha et al. (2024), we evaluate the robustness of the primary TOPSIS-CRITIC site suitability ranking "
    "across **12 criteria weight perturbation scenarios** spanning individual criterion shifts, equal weighting, "
    "transportation dominance, and commercial dominance."
)

st.markdown("---")

# Scale-Dependence Callout Box (S11 Road Sensitivity)
st.subheader(":material/search: Major Scale-Dependence Discovery (Scenario S11)")
st.warning(
    """
    **Scale-Dependent Road Proximity Dynamics (Scenario S11: 50% Road Weight):**
    * **Sample Scale (Central Varanasi, 6.75 km²):** Spearman correlation remained exceptionally high at **ρ = 0.9613** with a maximum site displacement of only 7 positions.
    * **Citywide Scale (Full Municipality, 76.99 km²):** Spearman correlation dropped sharply to **ρ = 0.7763** with maximum rank shifts exceeding 178 positions.
    * **Empirical Driver:** In the historic urban core, all candidate sites are situated close to arterial roads; at the full municipal scale, peripheral sites with low commercial/amenity density jump dozens of positions when road proximity is hyper-weighted. This proves that sensitivity dynamics are non-linearly scale-dependent.
    """
)

st.markdown("---")

# Sensitivity Tables & Comparison
tab_v2, tab_v1, tab_sample = st.tabs([
    "1. Full Citywide Mode v2 (Equal Scrutiny, 308 Sites)",
    "2. Full Citywide Mode v1 (Baseline, 308 Sites)",
    "3. Central Sample Mode (31 Sites)",
])

RENAME_COLS = {
    "scenario_id": "Scenario ID",
    "description": "Description",
    "perturbed_criterion": "Perturbed Criterion",
    "spearman_rho": "Spearman ρ",
    "kendall_tau": "Kendall τ",
    "top5_overlap_pct": "Top-5 Overlap (%)",
    "top10_overlap_pct": "Top-10 Overlap (%)",
    "max_rank_shift": "Max Shift",
}

FORMAT_DICT = {
    "Spearman ρ": "{:.4f}",
    "Kendall τ": "{:.4f}",
    "Top-5 Overlap (%)": "{:.1f}%",
    "Top-10 Overlap (%)": "{:.1f}%",
}

with tab_v2:
    sens_v2 = load_sensitivity_results("full_v2")
    st.markdown("**12-Scenario Perturbation Results (Milestone 7 Equal Scrutiny):**")
    
    col1, col2 = st.columns([1.4, 1.1])
    with col1:
        st.table(
            sens_v2.rename(columns=RENAME_COLS).style.format(FORMAT_DICT)
        )
    with col2:
        fig_bar = px.bar(
            sens_v2,
            x="scenario_id",
            y="spearman_rho",
            color="spearman_rho",
            color_continuous_scale="Viridis",
            labels={"scenario_id": "Scenario ID", "spearman_rho": "Spearman Correlation (ρ)"},
            title="Shortlist Stability Across All 12 Scenarios (v2)",
            text_auto=".3f",
        )
        fig_bar.update_layout(
            yaxis_range=[0.70, 1.05],
            xaxis=dict(type="category", tickmode="linear", dtick=1),
            margin=dict(l=20, r=20, t=40, b=20),
        )
        apply_plotly_theme(fig_bar)
        st.plotly_chart(fig_bar, width="stretch")

with tab_v1:
    sens_v1 = load_sensitivity_results("full_v1")
    st.markdown("**12-Scenario Perturbation Results (Milestone 6 Baseline):**")
    st.table(
        sens_v1.rename(columns=RENAME_COLS).style.format(FORMAT_DICT)
    )

with tab_sample:
    sens_sample = load_sensitivity_results("sample")
    st.markdown("**12-Scenario Perturbation Results (Sample Mode, Central Varanasi):**")
    st.table(
        sens_sample.rename(columns=RENAME_COLS).style.format(FORMAT_DICT)
    )

st.markdown("---")

# Visual Figure
st.subheader(":material/insights: Multi-Scenario Sensitivity Visualizations")
try:
    is_dark = st.session_state.get("theme") == "dark"
    fig_name = "mcdm_sensitivity_analysis_full_v2_dark.png" if is_dark else "mcdm_sensitivity_analysis_full_v2.png"
    fig_path = get_figure_path(fig_name)
    card_bg = "#161B22" if is_dark else "#FFFFFF"
    card_border = "#30363D" if is_dark else "#E2E8F0"
    st.markdown(
        f'<div style="background-color:{card_bg}; padding:12px; border-radius:8px; border:1px solid {card_border}; margin-bottom:12px;">',
        unsafe_allow_html=True,
    )
    st.image(
        Image.open(fig_path),
        caption="12-Scenario Sensitivity Analysis Curves: Spearman ρ and Shortlist Overlap (Citywide Equal-Scrutiny Mode)",
        width="stretch",
    )
    st.markdown("</div>", unsafe_allow_html=True)
except Exception as e:
    st.warning(f"Sensitivity figure not loaded: {e}")

