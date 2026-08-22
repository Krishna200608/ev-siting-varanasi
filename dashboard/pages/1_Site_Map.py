"""Page 1: Interactive Spatial Candidate Site Map."""

import sys
from pathlib import Path
import folium
from folium.plugins import Fullscreen
import streamlit as st
from streamlit_folium import st_folium

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.utils.data_loader import load_decision_matrix, load_mcdm_rankings, render_sidebar_logo
from dashboard.utils.theming import inject_theme_and_toggle, get_folium_tiles


st.set_page_config(page_title="Site Map — EV Siting Varanasi", page_icon=":material/map:", layout="wide")
inject_theme_and_toggle()
render_sidebar_logo()

st.title(":material/map: Interactive Spatial Candidate Site Map")
st.markdown(
    "Explore the spatial distribution of all **308 candidate alternatives** across the **76.99 km²** "
    "Varanasi municipal corporation extent. Candidate sites are evaluated on a regular 500m metric fishnet grid."
)

st.markdown("---")

# Version Selection Toggle
col_opt1, col_opt2 = st.columns([1, 3])
with col_opt1:
    version_choice = st.radio(
        "Select Spatial Measurement Version:",
        options=["v2 (Milestone 7: Equal Scrutiny)", "v1 (Milestone 6: Baseline)"],
        index=0,
        help="v2 incorporates equal 5-tile nested high-density measurement across Godowlia, Sigra, Lanka, and Cantt.",
    )
    version = "v2" if "v2" in version_choice else "v1"

with col_opt2:
    st.info(
        "**Visualization Legend:** Circles are sized and colored by TOPSIS-CRITIC suitability score "
        "(Dark Green = Highly Suitable, Yellow = Moderate, Red/Orange = Low). The **Top-5 Sites** are "
        "highlighted with gold-bordered crimson star markers.",
        icon=":material/info:",
    )

# Load data
rankings_df = load_mcdm_rankings(version)
matrix_df = load_decision_matrix(version)
merged_df = rankings_df.merge(matrix_df, on=["site_id", "latitude", "longitude"])

# Color helper
def get_marker_color(score: float) -> str:
    if score >= 0.70:
        return "#1b7837"  # Deep Green
    elif score >= 0.60:
        return "#7fbc41"  # Light Green
    elif score >= 0.50:
        return "#fee08b"  # Yellow
    elif score >= 0.40:
        return "#fdae61"  # Orange
    else:
        return "#d73027"  # Red


# Initialize Folium Map centered on Central Varanasi
map_center = [25.3120, 82.9950]
m = folium.Map(location=map_center, zoom_start=13, tiles=get_folium_tiles())
Fullscreen(position="topright").add_to(m)


# Add municipal bounds approx outline context
boundary_coords = [
    [25.265, 82.990], [25.268, 83.008], [25.285, 83.015], [25.305, 83.018],
    [25.325, 83.032], [25.340, 83.045], [25.362, 83.030], [25.368, 83.000],
    [25.365, 82.970], [25.345, 82.952], [25.320, 82.948], [25.298, 82.952],
    [25.282, 82.960], [25.268, 82.975], [25.265, 82.990]
]
folium.PolyLine(
    boundary_coords,
    color="#3182bd",
    weight=2.5,
    dash_array="5, 5",
    opacity=0.8,
    popup="Approximated VMC Municipal Boundary (~76.99 km²)",
).add_to(m)

# Plot Candidate Sites
top5_site_ids = set(rankings_df.sort_values("topsis_critic_rank").head(5)["site_id"])

for _, row in merged_df.iterrows():
    site_id = row["site_id"]
    lat, lon = row["latitude"], row["longitude"]
    rank = int(row["topsis_critic_rank"])
    score = float(row["topsis_critic_score"])

    # Detailed popup content
    popup_html = f"""
    <div style="font-family: Arial, sans-serif; min-width: 200px; font-size: 12px;">
        <h4 style="margin:0 0 5px 0; color: #1f77b4;"><b>{site_id}</b> (Rank #{rank})</h4>
        <b>TOPSIS-CRITIC Score:</b> {score:.4f}<br>
        <b>Coordinates:</b> {lat:.4f}°N, {lon:.4f}°E<br>
        <hr style="margin: 5px 0;">
        <b>Criteria Breakdown (1–9 Scale):</b><br>
        • Major Roads (C1): {row.get('C1_Major_Roads', 0):.2f}<br>
        • Competitor EVCS (C5): {row.get('C5_Competitor_EVCS', 0):.2f}<br>
        • Schools (C6): {row.get('C6_POI_Schools', 0):.2f}<br>
        • Shopping Malls (C6): {row.get('C6_POI_Shopping_Malls', 0):.2f}<br>
        • Restaurants (C6): {row.get('C6_POI_Restaurants', 0):.2f}<br>
        • Hospitals (C6): {row.get('C6_POI_Hospitals', 0):.2f}<br>
        • Theatres (C6): {row.get('C6_POI_Theatres', 0):.2f}<br>
        • Bus Stops (C6): {row.get('C6_POI_Bus_Stops', 0):.2f}<br>
        • Petrol Bunks (C6): {row.get('C6_POI_Petrol_Bunks', 0):.2f}
    </div>
    """

    if site_id in top5_site_ids:
        # Star marker for Top-5
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"⭐ Rank #{rank}: {site_id} (Score: {score:.4f})",
            icon=folium.Icon(color="red", icon="star", prefix="fa"),
        ).add_to(m)
    else:
        # Standard circle marker with theme-contrasting border
        color = get_marker_color(score)
        marker_border = "#ffffff" if st.session_state.get("theme") == "dark" else "#252525"
        folium.CircleMarker(
            location=[lat, lon],
            radius=4.5 + (score * 5),
            color=marker_border,
            weight=1.2,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"Rank #{rank}: {site_id} ({score:.4f})",
        ).add_to(m)


# Render Map in Streamlit
st_folium(m, width="100%", height=620, returned_objects=[])

# Top-5 Table Callout
st.subheader(f":material/trophy: Top-5 Ranked Charging Station Locations ({version_choice.split(':')[0]})")
top5_display = merged_df.sort_values("topsis_critic_rank").head(5)[[
    "site_id", "latitude", "longitude", "topsis_critic_score", "topsis_critic_rank",
    "C1_Major_Roads", "C6_POI_Shopping_Malls", "C6_POI_Restaurants", "C6_POI_Hospitals"
]]

st.dataframe(
    top5_display.rename(columns={
        "site_id": "Site ID",
        "latitude": "Latitude (°N)",
        "longitude": "Longitude (°E)",
        "topsis_critic_score": "TOPSIS Score",
        "topsis_critic_rank": "Rank",
        "C1_Major_Roads": "Major Roads (C1)",
        "C6_POI_Shopping_Malls": "Shopping Malls (C6)",
        "C6_POI_Restaurants": "Restaurants (C6)",
        "C6_POI_Hospitals": "Hospitals (C6)",
    }).style.format({
        "Latitude (°N)": "{:.4f}",
        "Longitude (°E)": "{:.4f}",
        "TOPSIS Score": "{:.4f}",
        "Major Roads (C1)": "{:.2f}",
        "Shopping Malls (C6)": "{:.2f}",
        "Restaurants (C6)": "{:.2f}",
        "Hospitals (C6)": "{:.2f}",
    }),
    width="stretch",
)

