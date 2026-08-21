"""Page 3: Live Interactive What-If Criteria Weight Explorer."""

import sys
from pathlib import Path
import plotly.express as px
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.utils.data_loader import load_decision_matrix, load_mcdm_rankings
from dashboard.utils.mcdm_live import (
    get_default_critic_weights,
    compute_live_whatif_ranking,
    CRITERIA_ORIENTATION,
)


st.set_page_config(page_title="What-If Explorer — EV Siting Varanasi", page_icon="🎛️", layout="wide")

st.title("🎛️ Live What-If Criteria Weight Explorer")
st.markdown(
    "Dynamically modify the importance weight of each spatial criterion and observe **real-time recalculations "
    "of the TOPSIS site suitability ranking** across all 308 candidate alternatives. "
    "Calculations are executed live using pure vector TOPSIS routines."
)

st.markdown("---")

# Load baseline data
dm_v2 = load_decision_matrix("v2")
base_rankings_v2 = load_mcdm_rankings("v2")
default_critic = get_default_critic_weights(dm_v2)

# Weight Preset Selector
st.subheader("⚡ Quick Weight Presets")
preset_cols = st.columns(5)

with preset_cols[0]:
    if st.button("📊 CRITIC Default (Empirical)", use_container_width=True):
        st.session_state["weights"] = default_critic.copy()

with preset_cols[1]:
    if st.button("⚖️ Equal Weights (1/9)", use_container_width=True):
        st.session_state["weights"] = {k: 1.0 / 9.0 for k in default_critic.keys()}

with preset_cols[2]:
    if st.button("🛣️ Road Arterial Focus (50% Road)", use_container_width=True):
        st.session_state["weights"] = {k: 0.50 if k == "C1_Major_Roads" else 0.50 / 8.0 for k in default_critic.keys()}

with preset_cols[3]:
    if st.button("🛍️ Retail Mall Focus (50% Malls)", use_container_width=True):
        st.session_state["weights"] = {k: 0.50 if k == "C6_POI_Shopping_Malls" else 0.50 / 8.0 for k in default_critic.keys()}

with preset_cols[4]:
    if st.button("🏥 Healthcare Focus (50% Hospital)", use_container_width=True):
        st.session_state["weights"] = {k: 0.50 if k == "C6_POI_Hospitals" else 0.50 / 8.0 for k in default_critic.keys()}

# Initialize session state if not set
if "weights" not in st.session_state:
    st.session_state["weights"] = default_critic.copy()

st.markdown("---")

# Sliders Section
st.subheader("🎚️ Custom Criteria Weight Adjusters")
st.caption(
    "Adjust raw slider values (weights are automatically normalized to sum to 1.0 before running TOPSIS). "
    "Note: Competitor EVCS is strictly evaluated as a **cost** criterion per project criteria standards."
)

col_s1, col_s2, col_s3 = st.columns(3)

criteria_keys = list(default_critic.keys())
slider_weights = {}

with col_s1:
    st.markdown("**Accessibility & Competition**")
    slider_weights["C1_Major_Roads"] = st.slider(
        "🛣️ Major Roads (C1) [Benefit]",
        min_value=0.0, max_value=1.0,
        value=float(st.session_state["weights"]["C1_Major_Roads"]),
        step=0.01,
    )
    slider_weights["C5_Competitor_EVCS"] = st.slider(
        "⚡ Competitor EVCS (C5) [Cost]",
        min_value=0.0, max_value=1.0,
        value=float(st.session_state["weights"]["C5_Competitor_EVCS"]),
        step=0.01,
        help="0 registered stations exist in Varanasi; weight scales competition avoidance.",
    )
    slider_weights["C6_POI_Schools"] = st.slider(
        "🏫 Schools & Universities (C6) [Benefit]",
        min_value=0.0, max_value=1.0,
        value=float(st.session_state["weights"]["C6_POI_Schools"]),
        step=0.01,
    )

with col_s2:
    st.markdown("**Commercial & Dining Density**")
    slider_weights["C6_POI_Shopping_Malls"] = st.slider(
        "🛍️ Shopping Malls & Retail (C6) [Benefit]",
        min_value=0.0, max_value=1.0,
        value=float(st.session_state["weights"]["C6_POI_Shopping_Malls"]),
        step=0.01,
    )
    slider_weights["C6_POI_Restaurants"] = st.slider(
        "🍽️ Restaurants & Dining (C6) [Benefit]",
        min_value=0.0, max_value=1.0,
        value=float(st.session_state["weights"]["C6_POI_Restaurants"]),
        step=0.01,
    )
    slider_weights["C6_POI_Theatres"] = st.slider(
        "🎬 Theatres & Cinemas (C6) [Benefit]",
        min_value=0.0, max_value=1.0,
        value=float(st.session_state["weights"]["C6_POI_Theatres"]),
        step=0.01,
    )

with col_s3:
    st.markdown("**Public Infrastructure & Transit**")
    slider_weights["C6_POI_Hospitals"] = st.slider(
        "🏥 Hospitals & Healthcare (C6) [Benefit]",
        min_value=0.0, max_value=1.0,
        value=float(st.session_state["weights"]["C6_POI_Hospitals"]),
        step=0.01,
    )
    slider_weights["C6_POI_Bus_Stops"] = st.slider(
        "🚌 Bus Stops & Transit (C6) [Benefit]",
        min_value=0.0, max_value=1.0,
        value=float(st.session_state["weights"]["C6_POI_Bus_Stops"]),
        step=0.01,
    )
    slider_weights["C6_POI_Petrol_Bunks"] = st.slider(
        "⛽ Petrol Bunks & Fuel (C6) [Benefit]",
        min_value=0.0, max_value=1.0,
        value=float(st.session_state["weights"]["C6_POI_Petrol_Bunks"]),
        step=0.01,
    )

# Compute live ranking
live_results = compute_live_whatif_ranking(
    custom_weights=slider_weights,
    decision_matrix_df=dm_v2,
    baseline_rankings_df=base_rankings_v2,
)

st.markdown("---")

# Display Outcomes & Metrics
st.subheader("🏆 Live Recomputed Top-10 Candidate Sites")

top1_site = live_results.iloc[0]
base_top1_site = base_rankings_v2.iloc[0]

metric_col1, metric_col2, metric_col3 = st.columns(3)
with metric_col1:
    st.metric(
        label="Top Ranked Alternative",
        value=str(top1_site["site_id"]),
        delta=f"Rank #{top1_site['custom_topsis_rank']}",
    )

with metric_col2:
    st.metric(
        label="Top TOPSIS Closeness Score",
        value=f"{top1_site['custom_topsis_score']:.4f}",
        delta=f"Δ {top1_site['custom_topsis_score'] - base_top1_site['topsis_critic_score']:+.4f} vs Baseline",
    )

with metric_col3:
    max_shift = int(live_results["rank_shift"].abs().max())
    st.metric(
        label="Max Citywide Rank Shift",
        value=f"{max_shift} Positions",
        help="Maximum displacement observed across all 308 candidate alternatives under this weight profile.",
    )

# Top 10 Table
top10_table = live_results.head(10)[[
    "site_id", "custom_topsis_rank", "baseline_rank", "rank_shift", "custom_topsis_score",
    "C1_Major_Roads", "C6_POI_Shopping_Malls", "C6_POI_Restaurants", "C6_POI_Hospitals"
]].rename(columns={
    "site_id": "Site ID",
    "custom_topsis_rank": "New Rank",
    "baseline_rank": "Baseline Rank",
    "rank_shift": "Rank Shift (Δ)",
    "custom_topsis_score": "New Score",
})

def format_shift(val: int) -> str:
    return f"+{val}" if val > 0 else str(val)

st.dataframe(
    top10_table.style.map(
        lambda v: "color: #4caf50; font-weight: bold;" if v > 0 else ("color: #ef5350; font-weight: bold;" if v < 0 else "color: #9e9e9e;"),
        subset=["Rank Shift (Δ)"],
    ).format({
        "New Score": "{:.4f}",
        "Rank Shift (Δ)": format_shift,
        "C1_Major_Roads": "{:.2f}",
        "C6_POI_Shopping_Malls": "{:.2f}",
        "C6_POI_Restaurants": "{:.2f}",
        "C6_POI_Hospitals": "{:.2f}",
    }),
    use_container_width=True,
)

st.markdown("---")

# Scatter comparison plot
st.subheader("📈 Baseline vs. Custom Rank Dispersal")
st.markdown("Points lying along the diagonal line represent candidate sites whose rank remains unchanged.")

fig = px.scatter(
    live_results,
    x="baseline_rank",
    y="custom_topsis_rank",
    hover_data=["site_id", "custom_topsis_score", "rank_shift"],
    color="rank_shift",
    color_continuous_scale="RdYlGn",
    labels={"baseline_rank": "Baseline TOPSIS-CRITIC Rank", "custom_topsis_rank": "Custom TOPSIS Rank", "rank_shift": "Rank Shift (Δ)"},
    title="Candidate Site Rank Stability Scatter Plot (308 Sites)",
)
fig.add_shape(
    type="line", line=dict(dash="dash", color="gray"),
    x0=1, y0=1, x1=308, y1=308
)
st.plotly_chart(fig, use_container_width=True)
