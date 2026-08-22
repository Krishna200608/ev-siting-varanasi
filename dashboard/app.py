"""Two-Stage EV Charging Station Siting Decision Support Framework — Varanasi, India.

Home Overview & Navigation Hub for Streamlit Showcase Dashboard.
"""

import sys
from pathlib import Path
import streamlit as st

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="EV Siting Varanasi — Decision Support Framework",
    page_icon=":material/electric_bolt:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add repository root to sys.path for internal imports
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.utils.data_loader import load_mcdm_rankings, render_sidebar_logo
from dashboard.utils.theming import inject_theme_and_toggle


def main() -> None:
    """Render the Main Overview & Navigation Page."""
    inject_theme_and_toggle()
    render_sidebar_logo()

    st.title(":material/electric_bolt: EV Charging Station Siting Decision Support Framework")
    st.markdown(
        "<p style='font-size: 1.05rem; opacity: 0.85; margin-top: -6px; margin-bottom: 20px; line-height: 1.5;'>"
        "A Two-Stage Spatial Multi-Criteria (GIS-MCDM) & Machine Learning Framework — Varanasi, India"
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Executive Summary
    st.subheader(":material/info: Project Overview & Two-Stage Architecture")
    st.markdown(
        """
        This decision support system addresses the critical urban planning and capital allocation challenge of 
        optimally siting public Electric Vehicle Fast-Charging Stations (EVCS) in **Varanasi, India**—an ancient, 
        densely populated, and rapidly electrifying urban ecosystem. 

        The framework establishes a rigorous, transparent **Two-Stage Architecture**:
        1. **Stage 1 (Spatial Suitability Ranking — *Where* to Site):** Ingests 9 verified spatial criteria 
           (arterial road networks, zero-competitor baseline, and 7 POI categories across 1,700+ verified locations) 
           evaluated on a metric 500m UTM Zone 44N fishnet grid clipped to the **76.99 km²** municipal corporation boundary. 
           Alternatives are ranked using **TOPSIS-CRITIC**, validated across WASPAS and Shannon Entropy formulations.
        2. **Stage 2 (Operational Demand Profiling — *When* Demand Occurs):** Leverages an empirical transferable 
           machine learning model trained on real EV telemetry (ACN-Data) to project 24-hour diurnal weekday vs. weekend 
           load profiles, informing operational scheduling, tariff design, and grid transformer sizing at prioritized sites.
        """
    )

    st.markdown("---")

    # Load baseline real data for headline metrics
    try:
        rankings_v2 = load_mcdm_rankings("v2")
        top_site = rankings_v2.iloc[0]
        top_site_id = str(top_site["site_id"])
        top_site_score = float(top_site["topsis_critic_score"])
        total_candidates = len(rankings_v2)
    except Exception:
        top_site_id = "SITE_195"
        top_site_score = 0.7459
        total_candidates = 308

    # Headline Stat Callouts
    st.subheader(":material/analytics: Key Urban & Decision Analytics Metrics")
    col1, col2, col3, col4 = st.columns(4, gap="medium")

    with col1:
        st.metric(
            label="Candidate Alternatives",
            value=f"{total_candidates} Sites",
            help="500m metric fishnet points strictly clipped to Varanasi Nagar Nigam municipal polygon (76.99 km²).",
        )

    with col2:
        st.metric(
            label="Existing Public Fast Chargers",
            value="0 Stations",
            delta="Unserved Greenfield Market",
            delta_color="off",
            help="Verified via OpenChargeMap API: zero operational public fast-charging stations registered within municipal bounds.",
        )

    with col3:
        st.metric(
            label="Top Ranked Site (TOPSIS)",
            value=top_site_id,
            delta="Godowlia / Girijaghar",
            delta_color="normal",
            help="Rank #1 across all 4 MCDM combinations (TOPSIS/WASPAS x CRITIC/Entropy).",
        )

    with col4:
        st.metric(
            label="Top Suitability Score",
            value=f"{top_site_score:.4f}",
            delta="+0.14 vs. Next Best Zone",
            delta_color="normal",
            help="Closeness coefficient on [0.0, 1.0] scale; significantly leads secondary nodes (Sigra: 0.6006, Cantt: 0.5384, Lanka: 0.5258).",
        )

    st.markdown("---")

    # Navigation Guide
    st.subheader(":material/explore: Interactive Dashboard Navigation")
    st.markdown("Explore the detailed components of the decision support framework using the sidebar:")

    nav_col1, nav_col2 = st.columns(2, gap="large")

    with nav_col1:
        st.markdown(
            """
            * **:material/map: 1. Site Map:** Interactive Folium map displaying all 308 candidate alternatives colored by suitability, 
              with Top-5 highlights and a Milestone 6 vs. Milestone 7 spatial measurement toggle.
            * **:material/leaderboard: 2. MCDM Rankings:** Searchable, sortable consolidated rankings table comparing TOPSIS and WASPAS 
              under objective CRITIC and Shannon Entropy weighting.
            * **:material/tune: 3. What-If Weight Explorer:** Live, interactive sensitivity tool with 9 sliders to recompute TOPSIS rankings 
              in real-time and observe rank shifts against the empirical baseline.
            * **:material/show_chart: 4. Demand & SHAP:** 24-hour diurnal charging load profiles, SHAP feature importance curves, and 
              methodological rationale on ML operational timing (RQ3).
            """
        )

    with nav_col2:
        st.markdown(
            """
            * **:material/query_stats: 5. Sensitivity Analysis:** 12-scenario criteria weight perturbation analysis and scale-dependent road 
              proximity dynamics (S11: ρ = 0.9613 → ρ = 0.7763).
            * **:material/verified_user: 6. Data Quality Audit:** Systematic 9-criteria × 2-version audit table, automated degeneracy safeguards, 
              and root-cause diagnostics.
            * **:material/menu_book: 7. Project Journey:** Chronological narrative of key architectural decisions (AD-1 through AD-11) documenting 
              methodological challenges, rejected shortcuts, and verified solutions.
            """
        )

    st.markdown("---")
    st.caption(
        "Developed by **Krishna Sikheriya** | Public Research Repository: "
        "[github.com/Krishna200608/ev-siting-varanasi](https://github.com/Krishna200608/ev-siting-varanasi)"
    )


# Configure Multi-Page Navigation with explicit "Home" title
pages = [
    st.Page(main, title="Home", icon=":material/home:", default=True),
    st.Page("pages/1_Site_Map.py", title="1. Site Map", icon=":material/map:"),
    st.Page("pages/2_MCDM_Rankings.py", title="2. MCDM Rankings", icon=":material/leaderboard:"),
    st.Page("pages/3_Whatif_Weight_Explorer.py", title="3. What-If Explorer", icon=":material/tune:"),
    st.Page("pages/4_Demand_and_SHAP.py", title="4. Demand & SHAP", icon=":material/show_chart:"),
    st.Page("pages/5_Sensitivity_Analysis.py", title="5. Sensitivity Analysis", icon=":material/query_stats:"),
    st.Page("pages/6_Data_Quality_Audit.py", title="6. Data Quality Audit", icon=":material/verified_user:"),
    st.Page("pages/7_Project_Journey.py", title="7. Project Journey", icon=":material/menu_book:"),
]

pg = st.navigation(pages)
pg.run()
