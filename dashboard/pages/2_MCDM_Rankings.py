"""Page 2: Multi-Criteria Siting Rankings Table & Method Comparison."""

import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.utils.data_loader import load_mcdm_rankings, render_sidebar_logo
from dashboard.utils.theming import inject_theme_and_toggle, apply_plotly_theme, get_top10_highlight_colors


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

# Filter and Version Selection Controls
col1, col2, col3 = st.columns([1.3, 1.3, 1.4], gap="medium")

with col1:
    version_choice = st.radio(
        "Measurement Version:",
        options=["v2 (Milestone 7: Equal Scrutiny)", "v1 (Milestone 6: Baseline)"],
        index=0,
    )
    version = "v2" if "v2" in version_choice else "v1"

# Load rankings dataset
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

# Candidate Count Indicator
st.markdown(f"**Showing {len(filtered_df):,} of {len(rankings_df):,} candidate alternatives**")

# Display Columns & Renaming
display_cols = [
    "site_id", "Urban Zone", "latitude", "longitude",
    "topsis_critic_rank", "topsis_critic_score",
    "waspas_critic_rank", "waspas_critic_score",
    "topsis_entropy_rank", "topsis_entropy_score",
    "waspas_entropy_rank", "waspas_entropy_score",
]

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

formatted_table = (
    filtered_df[display_cols]
    .rename(columns=rename_dict)
    .sort_values("TOPSIS-CRITIC Rank")
    .reset_index(drop=True)
)
formatted_table.insert(0, "S.No.", range(1, len(formatted_table) + 1))

is_dark = st.session_state.get("theme") == "dark"


def render_mcdm_rankings_table(df: pd.DataFrame, dark_mode: bool) -> str:
    """Generate clean, theme-aware responsive HTML table with light header in Light Mode."""
    th_bg = "#21262D" if dark_mode else "#F8F9FA"
    th_color = "#FAFAFA" if dark_mode else "#1E293B"
    th_border = "#30363D" if dark_mode else "#CBD5E1"

    top10_bg = "#14532D" if dark_mode else "#DCFCE7"
    top10_color = "#ECFDF5" if dark_mode else "#14532D"
    top10_border = "#1E3A2F" if dark_mode else "#BBF7D0"

    norm_bg = "#161B22" if dark_mode else "#FFFFFF"
    norm_color = "#FAFAFA" if dark_mode else "#1E293B"
    norm_border = "#30363D" if dark_mode else "#E2E8F0"

    rows_html = []
    for _, row in df.iterrows():
        is_top10 = row["TOPSIS-CRITIC Rank"] <= 10
        row_bg = top10_bg if is_top10 else norm_bg
        row_color = top10_color if is_top10 else norm_color
        row_border = top10_border if is_top10 else norm_border
        row_weight = "700" if is_top10 else "400"

        cells = [
            f"<td style='padding: 8px 12px; border: 1px solid {row_border}; text-align: center; font-weight: {row_weight};'>{int(row['S.No.'])}</td>",
            f"<td style='padding: 8px 12px; border: 1px solid {row_border}; text-align: left; font-weight: 700;'>{row['Site ID']}</td>",
            f"<td style='padding: 8px 12px; border: 1px solid {row_border}; text-align: left;'>{row['Urban Zone']}</td>",
            f"<td style='padding: 8px 12px; border: 1px solid {row_border}; text-align: right;'>{row['Latitude (°N)']:.4f}</td>",
            f"<td style='padding: 8px 12px; border: 1px solid {row_border}; text-align: right;'>{row['Longitude (°E)']:.4f}</td>",
            f"<td style='padding: 8px 12px; border: 1px solid {row_border}; text-align: center; font-weight: 700;'>{int(row['TOPSIS-CRITIC Rank'])}</td>",
            f"<td style='padding: 8px 12px; border: 1px solid {row_border}; text-align: right; font-weight: 700;'>{row['TOPSIS-CRITIC Score']:.4f}</td>",
            f"<td style='padding: 8px 12px; border: 1px solid {row_border}; text-align: center;'>{int(row['WASPAS-CRITIC Rank'])}</td>",
            f"<td style='padding: 8px 12px; border: 1px solid {row_border}; text-align: right;'>{row['WASPAS-CRITIC Score']:.4f}</td>",
            f"<td style='padding: 8px 12px; border: 1px solid {row_border}; text-align: center;'>{int(row['TOPSIS-Entropy Rank'])}</td>",
            f"<td style='padding: 8px 12px; border: 1px solid {row_border}; text-align: right;'>{row['TOPSIS-Entropy Score']:.4f}</td>",
            f"<td style='padding: 8px 12px; border: 1px solid {row_border}; text-align: center;'>{int(row['WASPAS-Entropy Rank'])}</td>",
            f"<td style='padding: 8px 12px; border: 1px solid {row_border}; text-align: right;'>{row['WASPAS-Entropy Score']:.4f}</td>",
        ]
        rows_html.append(f"<tr style='background-color: {row_bg}; color: {row_color}; font-size: 0.88rem;'>{''.join(cells)}</tr>")

    headers = [
        ("S.No.", "center"),
        ("Site ID", "left"),
        ("Urban Zone", "left"),
        ("Latitude (°N)", "right"),
        ("Longitude (°E)", "right"),
        ("TOPSIS-CRITIC Rank", "center"),
        ("TOPSIS-CRITIC Score", "right"),
        ("WASPAS-CRITIC Rank", "center"),
        ("WASPAS-CRITIC Score", "right"),
        ("TOPSIS-Entropy Rank", "center"),
        ("TOPSIS-Entropy Score", "right"),
        ("WASPAS-Entropy Rank", "center"),
        ("WASPAS-Entropy Score", "right"),
    ]

    th_cells = [
        f"<th style='padding: 10px 12px; background-color: {th_bg}; color: {th_color}; border: 1px solid {th_border}; font-weight: 600; text-align: {align}; font-size: 0.88rem; position: sticky; top: 0; z-index: 10; box-shadow: 0 1px 0 {th_border};'>{title}</th>"
        for title, align in headers
    ]

    return f"""
    <div style='width: 100%; max-height: 480px; overflow-y: auto; overflow-x: auto; border-radius: 8px; border: 1px solid {th_border}; margin-top: 10px; margin-bottom: 20px;'>
        <table style='width: 100%; border-collapse: collapse; white-space: nowrap; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;'>
            <thead>
                <tr>{''.join(th_cells)}</tr>
            </thead>
            <tbody>
                {''.join(rows_html)}
            </tbody>
        </table>
    </div>
    """


st.markdown(render_mcdm_rankings_table(formatted_table, is_dark), unsafe_allow_html=True)

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

# Inter-Method Rank Correlation Section
st.subheader(":material/query_stats: Inter-Method Rank Concordance & Correlation")
st.markdown(
    "Spearman's rank correlation (ρ) between algorithms confirms exceptional consensus, "
    "demonstrating that site prioritization is robust to algorithmic choice."
)

rank_cols = ["topsis_critic_rank", "waspas_critic_rank", "topsis_entropy_rank", "waspas_entropy_rank"]
corr_matrix = rankings_df[rank_cols].corr(method="spearman")
corr_matrix.columns = ["TOPSIS-CRITIC", "WASPAS-CRITIC", "TOPSIS-Entropy", "WASPAS-Entropy"]
corr_matrix.index = ["TOPSIS-CRITIC", "WASPAS-CRITIC", "TOPSIS-Entropy", "WASPAS-Entropy"]

is_dark = st.session_state.get("theme") == "dark"

# Professional Blue/Cyan Sequential Palette (0.95 -> 1.00 domain)
corr_colorscale = [
    [0.00, "#E8F4FA"],  # 0.9500 (very light blue)
    [0.25, "#90CAF9"],  # 0.9625 (lower-mid light blue)
    [0.50, "#29A3D1"],  # 0.9750 (mid cyan/blue)
    [0.75, "#0077B6"],  # 0.9875 (upper-mid royal blue)
    [1.00, "#005B8E"],  # 1.0000 (deep blue)
]

fig = go.Figure(
    data=go.Heatmap(
        z=corr_matrix.values,
        x=list(corr_matrix.columns),
        y=list(corr_matrix.index),
        colorscale=corr_colorscale,
        zmin=0.95,
        zmax=1.00,
        xgap=2,
        ygap=2,
        colorbar=dict(
            title=dict(
                text="Spearman ρ",
                font=dict(color="#FAFAFA" if is_dark else "#0F172A", size=13),
            ),
            tickvals=[0.95, 0.96, 0.97, 0.98, 0.99, 1.00],
            ticktext=["0.95", "0.96", "0.97", "0.98", "0.99", "1.00"],
            tickfont=dict(color="#FAFAFA" if is_dark else "#0F172A", size=11),
            len=0.90,
            thickness=18,
        ),
        hovertemplate=(
            "<b>Row:</b> %{y}<br>"
            "<b>Column:</b> %{x}<br>"
            "<b>Spearman ρ:</b> %{z:.4f}"
            "<extra></extra>"
        ),
    )
)

# Build high-contrast cell text annotations based on cell value luminance
annotations = []
for i, row in enumerate(corr_matrix.values):
    for j, val in enumerate(row):
        norm_val = (val - 0.95) / (1.00 - 0.95)
        # Deep blue cells (norm_val >= 0.45, val >= ~0.9725) get white text; light cells get dark navy text
        text_color = "#FFFFFF" if norm_val >= 0.45 else "#123047"
        
        annotations.append(
            dict(
                x=corr_matrix.columns[j],
                y=corr_matrix.index[i],
                text=f"<b>{val:.4f}</b>",
                showarrow=False,
                font=dict(
                    color=text_color,
                    size=13,
                    family="sans-serif",
                ),
            )
        )

fig.update_layout(
    annotations=annotations,
    title=dict(
        text=f"Spearman Rank Correlation Matrix ({version.upper()})",
        font=dict(color="#FAFAFA" if is_dark else "#0F172A", size=15),
    ),
    height=420,
    margin=dict(l=40, r=40, t=50, b=40),
    xaxis=dict(
        side="bottom",
        tickfont=dict(color="#FAFAFA" if is_dark else "#0F172A", size=12),
    ),
    yaxis=dict(
        autorange="reversed",
        tickfont=dict(color="#FAFAFA" if is_dark else "#0F172A", size=12),
    ),
)
apply_plotly_theme(fig)
st.plotly_chart(fig, width="stretch")
