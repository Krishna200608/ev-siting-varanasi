"""Page 2: Multi-Criteria Siting Rankings Table & Method Comparison."""

import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.utils.data_loader import load_mcdm_rankings, render_sidebar_logo
from dashboard.utils.theming import inject_theme_and_toggle, get_plotly_template, get_top10_highlight_colors


st.set_page_config(page_title="MCDM Rankings — EV Siting Varanasi", page_icon=":material/leaderboard:", layout="wide")
inject_theme_and_toggle()
render_sidebar_logo()

st.title(":material/leaderboard: Multi-Criteria Siting Rankings & Method Comparison")
st.markdown(
    "Analyze the comprehensive rankings across all **4 MCDM algorithmic combinations**: "
    "**TOPSIS** (Primary Ideal-Solution Benchmark) and **WASPAS** (Weighted Sum-Product Model) "
    "under **CRITIC** (Objective Variance & Contrast Intensity) and **Shannon Entropy** weighting."
)

st.markdown("---")

# Controls
col1, col2, col3 = st.columns([1.5, 1.5, 2])

with col1:
    version_choice = st.radio(
        "Measurement Version:",
        options=["v2 (Milestone 7: Equal Scrutiny)", "v1 (Milestone 6: Baseline)"],
        index=0,
    )
    version = "v2" if "v2" in version_choice else "v1"

# Load rankings
rankings_df = load_mcdm_rankings(version)

# Assign Urban Zones based on coordinates
def assign_urban_zone(row: pd.Series) -> str:
    lat, lon = row["latitude"], row["longitude"]
    if (25.300 <= lat <= 25.320) and (82.998 <= lon <= 83.015):
        return "Godowlia / Dashashwamedh Corridor"
    elif (25.302 <= lat <= 25.322) and (82.975 <= lon <= 82.992):
        return "Sigra Commercial Hub"
    elif (25.265 <= lat <= 25.292) and (82.988 <= lon <= 83.010):
        return "Lanka / BHU Road"
    elif (25.320 <= lat <= 25.342) and (82.970 <= lon <= 82.990):
        return "Cantonment Station & Market"
    else:
        return "Peri-Urban / Outer Wards"

rankings_df["Urban Zone"] = rankings_df.apply(assign_urban_zone, axis=1)

with col2:
    zone_options = ["All Zones"] + sorted(rankings_df["Urban Zone"].unique().tolist())
    selected_zone = st.selectbox("Filter by Urban Zone:", zone_options)

with col3:
    search_query = st.text_input("Search Site ID (e.g., SITE_195):", "").strip().upper()

# Apply filters
filtered_df = rankings_df.copy()
if selected_zone != "All Zones":
    filtered_df = filtered_df[filtered_df["Urban Zone"] == selected_zone]
if search_query:
    filtered_df = filtered_df[filtered_df["site_id"].str.contains(search_query)]

st.markdown(f"**Showing {len(filtered_df)} of {len(rankings_df)} candidate alternatives**")

# Display Table
display_cols = [
    "site_id", "Urban Zone", "latitude", "longitude",
    "topsis_critic_rank", "topsis_critic_score",
    "waspas_critic_rank", "waspas_critic_score",
    "topsis_entropy_rank", "topsis_entropy_score",
    "waspas_entropy_rank", "waspas_entropy_score",
]

# Rename for clean presentation
rename_dict = {
    "site_id": "Site ID",
    "latitude": "Latitude (°N)",
    "longitude": "Longitude (°E)",
    "topsis_critic_rank": "TOPSIS-CRITIC Rank",
    "topsis_critic_score": "TOPSIS-CRITIC Score",
    "waspas_critic_rank": "WASPAS-CRITIC Rank",
    "waspas_critic_score": "WASPAS-CRITIC Score",
    "topsis_entropy_rank": "TOPSIS-Entropy Rank",
    "topsis_entropy_score": "TOPSIS-Entropy Score",
    "waspas_entropy_rank": "WASPAS-Entropy Rank",
    "waspas_entropy_score": "WASPAS-Entropy Score",
}

formatted_table = filtered_df[display_cols].rename(columns=rename_dict).sort_values("TOPSIS-CRITIC Rank")

# Highlight Top-10
top10_style = get_top10_highlight_colors()

def highlight_top_10(row: pd.Series) -> list[str]:
    if row["TOPSIS-CRITIC Rank"] <= 10:
        return [f"background-color: {top10_style['bg']}; color: {top10_style['text']}; font-weight: bold;"] * len(row)
    return [""] * len(row)

st.dataframe(
    formatted_table.style.apply(highlight_top_10, axis=1).format({
        "Latitude (°N)": "{:.4f}",
        "Longitude (°E)": "{:.4f}",
        "TOPSIS-CRITIC Score": "{:.4f}",
        "WASPAS-CRITIC Score": "{:.4f}",
        "TOPSIS-Entropy Score": "{:.4f}",
        "WASPAS-Entropy Score": "{:.4f}",
    }),
    width="stretch",
    height=450,
)

# Download CSV
csv_data = formatted_table.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Filtered Rankings (CSV)",
    icon=":material/download:",
    data=csv_data,
    file_name=f"varanasi_ev_siting_rankings_{version}.csv",
    mime="text/csv",
)

st.markdown("---")

# Inter-Method Rank Correlation
st.subheader(":material/query_stats: Inter-Method Rank Concordance & Correlation")
st.markdown(
    "Spearman's rank correlation (ρ) between algorithms confirms exceptional consensus, "
    "demonstrating that site prioritization is robust to algorithmic choice."
)

rank_cols = ["topsis_critic_rank", "waspas_critic_rank", "topsis_entropy_rank", "waspas_entropy_rank"]
corr_matrix = rankings_df[rank_cols].corr(method="spearman")
corr_matrix.columns = ["TOPSIS-CRITIC", "WASPAS-CRITIC", "TOPSIS-Entropy", "WASPAS-Entropy"]
corr_matrix.index = ["TOPSIS-CRITIC", "WASPAS-CRITIC", "TOPSIS-Entropy", "WASPAS-Entropy"]

fig = px.imshow(
    corr_matrix,
    text_auto=".4f",
    color_continuous_scale="Viridis",
    title=f"Spearman Rank Correlation Matrix ({version.upper()})",
    aspect="auto",
)
fig.update_layout(
    font=dict(size=13),
    margin=dict(l=40, r=40, t=50, b=40),
    template=get_plotly_template(),
)
st.plotly_chart(fig, width="stretch")


