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

from dashboard.utils.data_loader import load_sensitivity_results, get_figure_path


st.set_page_config(page_title="Sensitivity Analysis — EV Siting Varanasi", page_icon=":material/query_stats:", layout="wide")

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

with tab_v2:
    sens_v2 = load_sensitivity_results("full_v2")
    st.markdown("**12-Scenario Perturbation Results (Milestone 7 Equal Scrutiny):**")
    
    col1, col2 = st.columns([1.4, 1.1])
    with col1:
        st.dataframe(
            sens_v2.rename(columns={
                "scenario_id": "Scenario ID",
                "description": "Description",
                "spearman_rho": "Spearman ρ",
                "kendall_tau": "Kendall τ",
                "top5_overlap_pct": "Top-5 Overlap (%)",
                "top10_overlap_pct": "Top-10 Overlap (%)",
                "max_rank_shift": "Max Shift",
            }).style.format({
                "Spearman ρ": "{:.4f}",
                "Kendall τ": "{:.4f}",
                "Top-5 Overlap (%)": "{:.1f}%",
                "Top-10 Overlap (%)": "{:.1f}%",
            }),
            use_container_width=True,
            height=430,
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
        st.plotly_chart(fig_bar, use_container_width=True)

with tab_v1:
    sens_v1 = load_sensitivity_results("full_v1")
    st.markdown("**12-Scenario Perturbation Results (Milestone 6 Baseline):**")
    st.dataframe(sens_v1, use_container_width=True)

with tab_sample:
    sens_sample = load_sensitivity_results("sample")
    st.markdown("**12-Scenario Perturbation Results (Sample Mode, Central Varanasi):**")
    st.dataframe(sens_sample, use_container_width=True)

st.markdown("---")

# Visual Figure
st.subheader(":material/insights: Multi-Scenario Sensitivity Visualizations")
try:
    fig_path = get_figure_path("mcdm_sensitivity_analysis_full_v2.png")
    st.image(
        Image.open(fig_path),
        caption="12-Scenario Sensitivity Analysis Curves: Spearman ρ, Kendall τ, and Shortlist Overlap (Citywide Mode)",
        use_container_width=True,
    )
except Exception as e:
    st.warning(f"Sensitivity figure not loaded: {e}")
