"""Page 4: Operational Demand Modeling, Temporal Curves & SHAP Explainability."""

import sys
from pathlib import Path
from PIL import Image
import pandas as pd
import plotly.express as px
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from dashboard.utils.data_loader import load_temporal_curve, get_figure_path, render_sidebar_logo


st.set_page_config(page_title="Demand & SHAP — EV Siting Varanasi", page_icon=":material/show_chart:", layout="wide")
render_sidebar_logo()

st.title(":material/show_chart: Operational Demand Profiling & SHAP Explainability")
st.markdown(
    "Stage 2 of the decision framework leverages empirical machine learning trained on **real EV charging session telemetry** "
    "(Caltech / JPL ACN-Data, $N=30,000+$ transactions) to model charging behavior, extract feature importance via SHAP, "
    "and project 24-hour diurnal operational load curves."
)

st.markdown("---")

# Section 1: Diurnal Demand Profiling
st.subheader(":material/schedule: 24-Hour Diurnal Energy Demand Profile")
st.markdown(
    "Projected expected charging demand (kWh/session) across the 24 hours of the day for **Weekdays vs. Weekends**. "
    "This profile provides grid operators and station developers with operational intelligence on *when* peak transformer "
    "stress and revenue-generating footfall occur."
)

# Load temporal curve
curve_df = load_temporal_curve()

# Create clean display copy for plotting
plot_curve_df = curve_df.rename(columns={
    "weekday_kwh": "Weekday Expected Load (kWh)",
    "weekend_kwh": "Weekend Expected Load (kWh)",
})

col_fig, col_tbl = st.columns([1.6, 1.1])

with col_fig:
    fig_demand = px.line(
        plot_curve_df,
        x="hour",
        y=["Weekday Expected Load (kWh)", "Weekend Expected Load (kWh)"],
        markers=True,
        labels={"hour": "Hour of Day (00:00 to 23:00)", "value": "Expected Energy (kWh / session)", "variable": "Session Day Type"},
        title="24-Hour Diurnal Energy Demand Curve (ACN-Data Transferable Model)",
        color_discrete_map={
            "Weekday Expected Load (kWh)": "#1f77b4",
            "Weekend Expected Load (kWh)": "#ff7f0e",
        },
    )
    fig_demand.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(tickmode="linear", tick0=0, dtick=2),
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    st.plotly_chart(fig_demand, use_container_width=True)

with col_tbl:
    st.markdown("**Diurnal Summary Metrics:**")
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.metric(
            label="Peak Hour (Weekday)",
            value="12:00 PM",
            delta="Midday Peak (17.77 kWh)",
            delta_color="off",
        )
    with m_col2:
        st.metric(
            label="Peak Hour (Weekend)",
            value="06:00 AM",
            delta="Morning Charge (29.18 kWh)",
            delta_color="off",
        )
    st.dataframe(curve_df.rename(columns={
        "hour": "Hour",
        "weekday_kwh": "Weekday (kWh)",
        "weekend_kwh": "Weekend (kWh)",
        "weighted_avg_kwh": "Weighted Avg (kWh)",
    }).style.format({
        "Weekday (kWh)": "{:.2f}",
        "Weekend (kWh)": "{:.2f}",
        "Weighted Avg (kWh)": "{:.2f}",
    }), height=270, use_container_width=True)

st.markdown("---")

# Section 2: SHAP Feature Explainability
st.subheader(":material/search: SHAP (SHapley Additive exPlanations) Feature Importance")

tab_full, tab_trans = st.tabs([
    "1. Full-Feature Model (General EV Behavior, R² ≈ 0.51)",
    "2. Transferable Temporal Model (Siting-Applicable, R² ≈ 0.02)"
])

with tab_full:
    st.markdown(
        """
        **Full-Feature XGBoost Model (Caltech/JPL ACN-Data):** Trained on session-level telemetry including 
        connection duration, charging duration, hour, day of week, and month ($R^2 = 0.5058$). 
        SHAP TreeExplainer reveals that **`charging_duration_hours` accounts for ~76.2% of predictive power**.
        """
    )
    col_sh1, col_sh2 = st.columns([1.5, 1])
    with col_sh1:
        try:
            img_path = get_figure_path("shap_summary.png")
            st.image(Image.open(img_path), caption="SHAP Summary Plot (Full-Feature ACN Model)", use_container_width=True)
        except Exception as e:
            st.error(f"Could not load image: {e}")
    with col_sh2:
        try:
            fi_path = REPO_ROOT / "outputs" / "tables" / "shap_feature_importance.csv"
            fi_df = pd.read_csv(fi_path)
            st.markdown("**Global Mean |SHAP| Values:**")
            st.dataframe(fi_df.rename(columns={"feature": "Feature", "mean_abs_shap": "Mean |SHAP|"}), use_container_width=True)
        except Exception as e:
            st.warning(f"Feature importance table not available: {e}")

with tab_trans:
    st.markdown(
        """
        **Transferable Temporal Model:** Formulated by strictly restricting features to observable temporal dimensions 
        (`connection_hour`, `day_of_week`, `is_weekend`, `month`). Because duration/dwell cannot be observed for an 
        unbuilt candidate site in Varanasi, this model prevents data fabrication while capturing temporal demand shape.
        """
    )
    col_tr1, col_tr2 = st.columns([1.5, 1])
    with col_tr1:
        try:
            img_path = get_figure_path("shap_summary_transferable.png")
            st.image(Image.open(img_path), caption="SHAP Summary Plot (Transferable Temporal Model)", use_container_width=True)
        except Exception as e:
            st.error(f"Could not load image: {e}")
    with col_tr2:
        try:
            fi_path = REPO_ROOT / "outputs" / "tables" / "shap_feature_importance_transferable.csv"
            fi_df = pd.read_csv(fi_path)
            st.markdown("**Global Mean |SHAP| Values:**")
            st.dataframe(fi_df.rename(columns={"feature": "Feature", "mean_abs_shap": "Mean |SHAP|"}), use_container_width=True)
        except Exception as e:
            st.warning(f"Feature importance table not available: {e}")

st.markdown("---")

# Section 3: Methodological Rationale (AD-8 / RQ3)
st.subheader(":material/psychology: Methodological Resolution of Research Question 3 (RQ3)")
st.info(
    """
    **Why ML Demand Informs *Operational Timing* Rather Than *Spatial Site Selection*:**
    * **The Spatial Independence Trap (AD-5 / AD-8):** Temporal ML models predict identical 24-hour demand curves for every 
      geographical coordinate. Combining temporal ML scalars multiplicatively with spatial footfall produces mathematically 
      inert rankings (canceling out upon min-max normalization).
    * **Zero-Fabrication Discipline (AD-6):** Fabricating arbitrary dwell-time proxies (e.g. 3.5h for malls, 0.75h for fuel bunks) 
      would artificially generate spatial differentiation from invented numbers, violating scientific integrity.
    * **The Two-Stage Solution:** Spatial site ranking (*Where*) is governed strictly by the Stage 1 GIS-MCDM TOPSIS framework, 
      while Machine Learning (*When*) governs operational load scheduling, dynamic tariffs, and grid transformer sizing at prioritized sites.
    """,
    icon=":material/lightbulb:",
)
