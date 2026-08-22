"""Page 1: Interactive Spatial Candidate Site Map."""

import sys
from pathlib import Path
import folium
from folium.plugins import Fullscreen
import pandas as pd
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

# Version Selection Toggle & Visualization Legend
col_opt1, col_opt2 = st.columns([1.1, 2.9], gap="medium")
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

is_dark = st.session_state.get("theme") == "dark"


@st.cache_resource(show_spinner=False)
def get_cached_site_map(version_key: str, dark_mode: bool) -> folium.Map:
    """Build and cache the complete interactive Folium candidate site map."""
    rankings_data = load_mcdm_rankings(version_key)
    matrix_data = load_decision_matrix(version_key)
    merged_data = rankings_data.merge(
        matrix_data.drop(columns=["latitude", "longitude"], errors="ignore"),
        on="site_id",
    )

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

    map_center = [25.3120, 82.9950]
    tiles = "CartoDB dark_matter" if dark_mode else "CartoDB positron"
    folium_map = folium.Map(location=map_center, zoom_start=13, tiles=tiles)
    Fullscreen(position="topright").add_to(folium_map)

    # Municipal bounds approx outline context
    boundary_coords = [
        [25.265, 82.990], [25.268, 83.008], [25.285, 83.015], [25.305, 83.018],
        [25.325, 83.032], [25.340, 83.045], [25.362, 83.030], [25.368, 83.000],
        [25.365, 82.970], [25.345, 82.952], [25.320, 82.948], [25.298, 82.952],
        [25.282, 82.960], [25.268, 82.975], [25.265, 82.990]
    ]
    boundary_color = "#38BDF8" if dark_mode else "#0284C7"
    folium.PolyLine(
        boundary_coords,
        color=boundary_color,
        weight=2.5,
        dash_array="6, 6",
        opacity=0.85,
        popup="Approximated VMC Municipal Boundary (~76.99 km²)",
    ).add_to(folium_map)

    top5_ids = set(rankings_data.sort_values("topsis_critic_rank").head(5)["site_id"])

    popup_bg = "#161B22" if dark_mode else "#FFFFFF"
    popup_text = "#FAFAFA" if dark_mode else "#1E293B"
    popup_accent = "#38BDF8" if dark_mode else "#0284C7"
    popup_hr = "#30363D" if dark_mode else "#E2E8F0"

    for _, row in merged_data.iterrows():
        site_id = row["site_id"]
        lat, lon = row["latitude"], row["longitude"]
        rank = int(row["topsis_critic_rank"])
        score = float(row["topsis_critic_score"])

        popup_html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 200px; font-size: 12px; color: {popup_text}; background-color: {popup_bg}; padding: 2px;">
            <h4 style="margin:0 0 5px 0; color: {popup_accent};"><b>{site_id}</b> (Rank #{rank})</h4>
            <b>TOPSIS-CRITIC Score:</b> {score:.4f}<br>
            <b>Coordinates:</b> {lat:.4f}°N, {lon:.4f}°E<br>
            <hr style="margin: 5px 0; border: none; border-top: 1px solid {popup_hr};">
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

        if site_id in top5_ids:
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"⭐ Rank #{rank}: {site_id} (Score: {score:.4f})",
                icon=folium.Icon(color="red", icon="star", prefix="fa"),
            ).add_to(folium_map)
        else:
            color = get_marker_color(score)
            marker_border = "#ffffff" if dark_mode else "#334155"
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
            ).add_to(folium_map)

    return folium_map


# Retrieve cached Folium Map
m = get_cached_site_map(version, is_dark)

# Render Map in Streamlit with dynamic key
st_folium(
    m,
    key=f"cached_site_map_{version}_{'dark' if is_dark else 'light'}",
    use_container_width=True,
    height=620,
    returned_objects=[],
)

# Load data for Top-5 Table
rankings_df = load_mcdm_rankings(version)
matrix_df = load_decision_matrix(version)
merged_df = rankings_df.merge(matrix_df.drop(columns=["latitude", "longitude"], errors="ignore"), on="site_id")

# Top-5 Table Callout
st.subheader(f":material/trophy: Top-5 Ranked Charging Station Locations ({version_choice.split(':')[0]})")
top5_display = merged_df.sort_values("topsis_critic_rank").head(5)[[
    "site_id", "latitude", "longitude", "topsis_critic_score", "topsis_critic_rank",
    "C1_Major_Roads", "C6_POI_Shopping_Malls", "C6_POI_Restaurants", "C6_POI_Hospitals"
]].copy()

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
}, inplace=True)


def render_top5_table(df: pd.DataFrame, dark_mode: bool) -> str:
    """Generate clean, theme-aware responsive HTML table with light header in Light Mode."""
    th_bg = "#21262D" if dark_mode else "#F8F9FA"
    th_color = "#FAFAFA" if dark_mode else "#1E293B"
    th_border = "#30363D" if dark_mode else "#CBD5E1"

    td_bg = "#14532D" if dark_mode else "#DCFCE7"
    td_color = "#ECFDF5" if dark_mode else "#14532D"
    td_border = "#1E3A2F" if dark_mode else "#BBF7D0"

    rows_html = []
    for _, row in df.iterrows():
        cells = [
            f"<td style='padding: 10px 14px; border: 1px solid {td_border}; font-weight: 700; text-align: left;'>{row['Site ID']}</td>",
            f"<td style='padding: 10px 14px; border: 1px solid {td_border}; text-align: right;'>{row['Latitude (°N)']:.4f}</td>",
            f"<td style='padding: 10px 14px; border: 1px solid {td_border}; text-align: right;'>{row['Longitude (°E)']:.4f}</td>",
            f"<td style='padding: 10px 14px; border: 1px solid {td_border}; font-weight: 700; text-align: right;'>{row['TOPSIS Score']:.4f}</td>",
            f"<td style='padding: 10px 14px; border: 1px solid {td_border}; font-weight: 700; text-align: center;'>{int(row['Rank'])}</td>",
            f"<td style='padding: 10px 14px; border: 1px solid {td_border}; text-align: right;'>{row['Major Roads (C1)']:.2f}</td>",
            f"<td style='padding: 10px 14px; border: 1px solid {td_border}; text-align: right;'>{row['Shopping Malls (C6)']:.2f}</td>",
            f"<td style='padding: 10px 14px; border: 1px solid {td_border}; text-align: right;'>{row['Restaurants (C6)']:.2f}</td>",
            f"<td style='padding: 10px 14px; border: 1px solid {td_border}; text-align: right;'>{row['Hospitals (C6)']:.2f}</td>",
        ]
        rows_html.append(f"<tr style='background-color: {td_bg}; color: {td_color}; font-size: 0.92rem;'>{''.join(cells)}</tr>")

    headers = [
        ("Site ID", "left"),
        ("Latitude (°N)", "right"),
        ("Longitude (°E)", "right"),
        ("TOPSIS Score", "right"),
        ("Rank", "center"),
        ("Major Roads (C1)", "right"),
        ("Shopping Malls (C6)", "right"),
        ("Restaurants (C6)", "right"),
        ("Hospitals (C6)", "right"),
    ]

    th_cells = [
        f"<th style='padding: 10px 14px; background-color: {th_bg}; color: {th_color}; border: 1px solid {th_border}; font-weight: 600; text-align: {align}; font-size: 0.92rem;'>{title}</th>"
        for title, align in headers
    ]

    return f"""
    <div style='width: 100%; overflow-x: auto; border-radius: 8px; border: 1px solid {th_border}; margin-top: 10px; margin-bottom: 20px;'>
        <table style='width: 100%; border-collapse: collapse; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;'>
            <thead>
                <tr>{''.join(th_cells)}</tr>
            </thead>
            <tbody>
                {''.join(rows_html)}
            </tbody>
        </table>
    </div>
    """


st.markdown(render_top5_table(top5_display, is_dark), unsafe_allow_html=True)
