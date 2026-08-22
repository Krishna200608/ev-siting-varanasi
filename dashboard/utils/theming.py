"""Runtime light/dark theme toggle: session_state, CSS injection, and chart/map re-theming helpers for the multipage dashboard."""

import streamlit as st

LIGHT_CSS = """
<style>
/* Base App & Header */
.stApp, [data-testid="stAppViewContainer"] {
    background-color: #FFFFFF;
    color: #1A1A1A;
}
header[data-testid="stHeader"], [data-testid="stHeader"] {
    background-color: #FFFFFF !important;
}

/* Sidebar Navigation */
[data-testid="stSidebar"] {
    background-color: #F8F9FA !important;
    border-right: 1px solid #E9ECEF;
}
[data-testid="stSidebarNav"] {
    background-color: transparent !important;
}
[data-testid="stSidebarNav"] a,
[data-testid="stSidebarNav"] span,
[data-testid="stSidebarNavLink"],
[data-testid="stSidebarNavLink"] span,
[data-testid="stSidebar"] [data-testid="stSidebarNav"] span,
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a,
[data-testid="stSidebar"] > div p {
    color: #1E293B !important;
    font-weight: 500 !important;
}
[data-testid="stSidebarNav"] a:hover,
[data-testid="stSidebarNav"] a:hover span,
[data-testid="stSidebarNavLink"]:hover span {
    color: #0284C7 !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"],
[data-testid="stSidebarNav"] a[aria-current="page"] span,
[data-testid="stSidebarNavLink"][aria-current="page"] span {
    color: #0284C7 !important;
    font-weight: 700 !important;
}

/* Buttons */
[data-testid="stSidebar"] button,
button[kind="secondary"],
[data-testid="baseButton-secondary"] {
    background-color: #FFFFFF !important;
    border: 1px solid #D0D7DE !important;
    color: #1E293B !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] button:hover,
button[kind="secondary"]:hover,
[data-testid="baseButton-secondary"]:hover {
    background-color: #F3F4F6 !important;
    border-color: #94A3B8 !important;
}
[data-testid="stSidebar"] button p,
[data-testid="stSidebar"] button span,
[data-testid="stSidebar"] button svg,
button[kind="secondary"] p,
button[kind="secondary"] span,
button[kind="secondary"] svg,
[data-testid="baseButton-secondary"] p,
[data-testid="baseButton-secondary"] span,
[data-testid="baseButton-secondary"] svg {
    color: #1E293B !important;
    fill: #1E293B !important;
    font-weight: 500 !important;
}

/* Metric Cards */
[data-testid="stMetric"] {
    background-color: #F8F9FA !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    padding: 14px !important;
}
[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] span,
[data-testid="stMetricLabel"] * {
    color: #475569 !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
}
[data-testid="stMetricValue"] div,
[data-testid="stMetricValue"] span,
[data-testid="stMetricValue"] * {
    color: #0F172A !important;
    font-weight: 700 !important;
}
[data-testid="stMetricDelta"],
[data-testid="stMetricDelta"] div,
[data-testid="stMetricDelta"] span,
[data-testid="stMetricDelta"] p,
[data-testid="stMetricDelta"] svg {
    color: #334155 !important;
    fill: #334155 !important;
    font-weight: 600 !important;
}
[data-testid="stMetricDelta"] {
    background-color: #E2E8F0 !important;
    border-radius: 6px !important;
    padding: 2px 8px !important;
    display: inline-flex !important;
    align-items: center !important;
}

/* Dataframe and Tables */
[data-testid="stDataFrame"] {
    background-color: #FFFFFF !important;
}
[data-testid="stTable"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}
[data-testid="stTable"] table {
    background-color: #FFFFFF !important;
    color: #334155 !important;
    border-collapse: collapse !important;
    width: 100% !important;
}
[data-testid="stTable"] th {
    background-color: #F8F9FA !important;
    color: #1E293B !important;
    border: 1px solid #E2E8F0 !important;
    font-weight: 600 !important;
    padding: 8px 12px !important;
}
[data-testid="stTable"] td {
    background-color: #FFFFFF !important;
    color: #334155 !important;
    border: 1px solid #E2E8F0 !important;
    padding: 8px 12px !important;
}
[data-testid="stTable"] tr:hover td {
    background-color: #F1F5F9 !important;
}

/* Expanders */
[data-testid="stExpander"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary {
    background-color: #F8F9FA !important;
    color: #1E293B !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary:hover {
    background-color: #F1F5F9 !important;
}
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary svg {
    color: #1E293B !important;
    fill: #1E293B !important;
    font-weight: 600 !important;
}
[data-testid="stExpanderDetails"] {
    background-color: #FFFFFF !important;
    color: #334155 !important;
    border-top: 1px solid #E2E8F0 !important;
}

/* Callout Alerts */
[data-testid="stAlert"] {
    border-radius: 8px !important;
}
[data-testid="stAlert"] * {
    color: #1E293B !important;
}
[data-testid="stAlert"] strong {
    color: #0F172A !important;
    font-weight: 700 !important;
}
[data-testid="stAlert"] code {
    color: #0F172A !important;
    background-color: rgba(0, 0, 0, 0.06) !important;
}

/* Tabs (st.tabs & React-Aria Tabs in Light Mode) */
[data-testid="stTabs"],
div[data-testid="stTabs"] {
    border-bottom: 2px solid #E2E8F0 !important;
}
div[data-testid="stTab"],
[data-testid="stTab"],
div[role="tab"],
button[data-baseweb="tab"] {
    color: #475569 !important;
    background-color: transparent !important;
    border: none !important;
    padding: 8px 16px !important;
    font-weight: 500 !important;
}
div[data-testid="stTab"] [data-testid="stMarkdownContainer"] p,
div[data-testid="stTab"] p,
div[data-testid="stTab"] span,
button[data-baseweb="tab"] p,
button[data-baseweb="tab"] div {
    color: #475569 !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
}
div[data-testid="stTab"]:hover,
div[data-testid="stTab"]:hover p,
button[data-baseweb="tab"]:hover {
    color: #0F172A !important;
    font-weight: 600 !important;
}
div[data-testid="stTab"][aria-selected="true"],
div[data-testid="stTab"][data-selected="true"],
div[role="tab"][aria-selected="true"],
button[data-baseweb="tab"][aria-selected="true"] {
    color: #0284C7 !important;
}
div[data-testid="stTab"][aria-selected="true"] [data-testid="stMarkdownContainer"] p,
div[data-testid="stTab"][data-selected="true"] p,
button[data-baseweb="tab"][aria-selected="true"] p {
    color: #0284C7 !important;
    font-weight: 700 !important;
}
.react-aria-SelectionIndicator,
div[data-testid="stTab"] .react-aria-SelectionIndicator {
    background-color: #0284C7 !important;
    border-color: #0284C7 !important;
    height: 3px !important;
    border-radius: 2px !important;
}

/* Code Blocks & Inline Code */
pre,
[data-testid="stCode"],
[data-testid="stCodeBlock"],
.stCode,
.stCode pre {
    background-color: #F8F9FA !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    color: #0F172A !important;
}
pre code,
[data-testid="stCode"] code,
.stCode code {
    background-color: transparent !important;
    color: #0F172A !important;
    border: none !important;
}
code {
    background-color: #F1F5F9 !important;
    color: #0F172A !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-size: 0.88em !important;
    border: 1px solid #E2E8F0 !important;
}

/* Divider Line */
hr {
    border-color: #E2E8F0 !important;
}
</style>
"""

DARK_CSS = """
<style>
/* Base App & Header */
.stApp, [data-testid="stAppViewContainer"] {
    background-color: #0E1117;
    color: #FAFAFA;
}
header[data-testid="stHeader"], [data-testid="stHeader"] {
    background-color: #0E1117 !important;
}

/* Sidebar Navigation */
[data-testid="stSidebar"] {
    background-color: #161B22 !important;
    border-right: 1px solid #30363D;
}
[data-testid="stSidebarNav"] {
    background-color: transparent !important;
}
[data-testid="stSidebarNav"] a,
[data-testid="stSidebarNav"] span,
[data-testid="stSidebarNavLink"],
[data-testid="stSidebarNavLink"] span,
[data-testid="stSidebar"] [data-testid="stSidebarNav"] span,
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a,
[data-testid="stSidebar"] > div p {
    color: #E6EDF3 !important;
    font-weight: 500 !important;
}
[data-testid="stSidebarNav"] a:hover,
[data-testid="stSidebarNav"] a:hover span,
[data-testid="stSidebarNavLink"]:hover span {
    color: #58A6FF !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"],
[data-testid="stSidebarNav"] a[aria-current="page"] span,
[data-testid="stSidebarNavLink"][aria-current="page"] span {
    color: #58A6FF !important;
    font-weight: 700 !important;
}

/* Buttons */
[data-testid="stSidebar"] button,
button[kind="secondary"],
[data-testid="baseButton-secondary"] {
    background-color: #21262D !important;
    border: 1px solid #30363D !important;
    color: #FAFAFA !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] button:hover,
button[kind="secondary"]:hover,
[data-testid="baseButton-secondary"]:hover {
    background-color: #30363D !important;
    border-color: #8B949E !important;
}
[data-testid="stSidebar"] button p,
[data-testid="stSidebar"] button span,
[data-testid="stSidebar"] button svg,
button[kind="secondary"] p,
button[kind="secondary"] span,
button[kind="secondary"] svg,
[data-testid="baseButton-secondary"] p,
[data-testid="baseButton-secondary"] span,
[data-testid="baseButton-secondary"] svg {
    color: #FAFAFA !important;
    fill: #FAFAFA !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] button:hover p,
[data-testid="stSidebar"] button:hover span,
[data-testid="stSidebar"] button:hover svg {
    color: #58A6FF !important;
    fill: #58A6FF !important;
}

/* Metric Cards */
[data-testid="stMetric"] {
    background-color: #161B22 !important;
    border: 1px solid #30363D !important;
    border-radius: 8px !important;
    padding: 14px !important;
}
[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] span,
[data-testid="stMetricLabel"] * {
    color: #8B949E !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
}
[data-testid="stMetricValue"] div,
[data-testid="stMetricValue"] span,
[data-testid="stMetricValue"] * {
    color: #58A6FF !important;
    font-weight: 700 !important;
}
[data-testid="stMetricDelta"],
[data-testid="stMetricDelta"] div,
[data-testid="stMetricDelta"] span,
[data-testid="stMetricDelta"] p,
[data-testid="stMetricDelta"] svg {
    color: #E6EDF3 !important;
    fill: #E6EDF3 !important;
    font-weight: 600 !important;
}
[data-testid="stMetricDelta"] {
    background-color: #21262D !important;
    border-radius: 6px !important;
    padding: 2px 8px !important;
    display: inline-flex !important;
    align-items: center !important;
}

/* Dataframe and Tables */
[data-testid="stDataFrame"] {
    background-color: #0E1117 !important;
}
[data-testid="stTable"] {
    background-color: #161B22 !important;
    border: 1px solid #30363D !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}
[data-testid="stTable"] table {
    background-color: #161B22 !important;
    color: #FAFAFA !important;
    border-collapse: collapse !important;
    width: 100% !important;
}
[data-testid="stTable"] th {
    background-color: #21262D !important;
    color: #FAFAFA !important;
    border: 1px solid #30363D !important;
    font-weight: 600 !important;
    padding: 8px 12px !important;
}
[data-testid="stTable"] td {
    background-color: #161B22 !important;
    color: #FAFAFA !important;
    border: 1px solid #30363D !important;
    padding: 8px 12px !important;
}
[data-testid="stTable"] tr:hover td {
    background-color: #1C222B !important;
}

/* Expanders */
[data-testid="stExpander"] {
    background-color: #161B22 !important;
    border: 1px solid #30363D !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary {
    background-color: #161B22 !important;
    color: #FAFAFA !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary:hover {
    background-color: #21262D !important;
}
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary svg {
    color: #FAFAFA !important;
    fill: #FAFAFA !important;
    font-weight: 600 !important;
}
[data-testid="stExpanderDetails"] {
    background-color: #0E1117 !important;
    color: #FAFAFA !important;
    border-top: 1px solid #30363D !important;
}
[data-testid="stExpanderDetails"] p,
[data-testid="stExpanderDetails"] li {
    color: #E6EDF3 !important;
}
[data-testid="stExpanderDetails"] strong {
    color: #FFFFFF !important;
}

/* Callout Alerts */
[data-testid="stAlert"] {
    border-radius: 8px !important;
}
[data-testid="stAlert"] * {
    color: #E6EDF3 !important;
}
[data-testid="stAlert"] strong {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}
[data-testid="stAlert"] code {
    color: #79C0FF !important;
    background-color: rgba(255, 255, 255, 0.08) !important;
}

/* Tabs (st.tabs & React-Aria Tabs in Dark Mode) */
[data-testid="stTabs"],
div[data-testid="stTabs"] {
    border-bottom: 2px solid #30363D !important;
}
div[data-testid="stTab"],
[data-testid="stTab"],
div[role="tab"],
button[data-baseweb="tab"] {
    color: #8B949E !important;
    background-color: transparent !important;
    border: none !important;
    padding: 8px 16px !important;
    font-weight: 500 !important;
}
div[data-testid="stTab"] [data-testid="stMarkdownContainer"] p,
div[data-testid="stTab"] p,
div[data-testid="stTab"] span,
button[data-baseweb="tab"] p,
button[data-baseweb="tab"] div {
    color: #8B949E !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
}
div[data-testid="stTab"]:hover,
div[data-testid="stTab"]:hover p,
button[data-baseweb="tab"]:hover {
    color: #FAFAFA !important;
    font-weight: 600 !important;
}
div[data-testid="stTab"][aria-selected="true"],
div[data-testid="stTab"][data-selected="true"],
div[role="tab"][aria-selected="true"],
button[data-baseweb="tab"][aria-selected="true"] {
    color: #58A6FF !important;
}
div[data-testid="stTab"][aria-selected="true"] [data-testid="stMarkdownContainer"] p,
div[data-testid="stTab"][data-selected="true"] p,
button[data-baseweb="tab"][aria-selected="true"] p {
    color: #58A6FF !important;
    font-weight: 700 !important;
}
.react-aria-SelectionIndicator,
div[data-testid="stTab"] .react-aria-SelectionIndicator {
    background-color: #58A6FF !important;
    border-color: #58A6FF !important;
    height: 3px !important;
    border-radius: 2px !important;
}

/* Code Blocks & Inline Code */
pre,
[data-testid="stCode"],
[data-testid="stCodeBlock"],
.stCode,
.stCode pre {
    background-color: #161B22 !important;
    border: 1px solid #30363D !important;
    border-radius: 8px !important;
    color: #E6EDF3 !important;
}
pre code,
[data-testid="stCode"] code,
.stCode code {
    background-color: transparent !important;
    color: #E6EDF3 !important;
    border: none !important;
}
[data-testid="stCode"] button,
.stCode button {
    background-color: #21262D !important;
    color: #8B949E !important;
    border: 1px solid #30363D !important;
}
code {
    background-color: #21262D !important;
    color: #79C0FF !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-size: 0.88em !important;
    border: 1px solid #30363D !important;
}

/* Divider Line */
hr {
    border-color: #30363D !important;
}
</style>
"""


def inject_theme_and_toggle() -> None:
    """Inject theme CSS and render the sidebar theme toggle button.
    
    Call at the top of every page (app.py + all files in pages/).
    """
    if "theme" not in st.session_state:
        st.session_state.theme = "light"

    st.markdown(
        DARK_CSS if st.session_state.theme == "dark" else LIGHT_CSS,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        is_light = st.session_state.theme == "light"
        icon = ":material/dark_mode:" if is_light else ":material/light_mode:"
        label = "Dark Mode" if is_light else "Light Mode"
        if st.button(label, icon=icon, key="theme_toggle_btn", width="stretch"):
            st.session_state.theme = "dark" if is_light else "light"
            st.rerun()


def get_plotly_template() -> str:
    """Return Plotly template string according to current theme."""
    return "plotly_dark" if st.session_state.get("theme") == "dark" else "plotly_white"


def get_plotly_layout_defaults() -> dict:
    """Return standard plotly layout configuration for the active theme."""
    if st.session_state.get("theme") == "dark":
        return dict(
            template="plotly_dark",
            paper_bgcolor="#0E1117",
            plot_bgcolor="#161B22",
            font=dict(color="#FAFAFA", family="sans-serif"),
        )
    return dict(
        template="plotly_white",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#0F172A", family="sans-serif"),
    )


def apply_plotly_theme(fig) -> None:
    """Apply comprehensive theme-aware styling to any Plotly figure."""
    is_dark = st.session_state.get("theme") == "dark"
    if is_dark:
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0E1117",
            plot_bgcolor="#161B22",
            font=dict(color="#FAFAFA", family="sans-serif"),
            title_font=dict(color="#FAFAFA", size=15),
            legend=dict(
                font=dict(color="#FAFAFA", size=12),
                title=dict(font=dict(color="#FAFAFA", size=12)),
            ),
        )
        fig.update_xaxes(
            title_font=dict(color="#FAFAFA", size=13),
            tickfont=dict(color="#E6EDF3", size=11),
            gridcolor="#30363D",
            linecolor="#30363D",
        )
        fig.update_yaxes(
            title_font=dict(color="#FAFAFA", size=13),
            tickfont=dict(color="#E6EDF3", size=11),
            gridcolor="#30363D",
            linecolor="#30363D",
        )
    else:
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(color="#0F172A", family="sans-serif"),
            title_font=dict(color="#0F172A", size=15),
            legend=dict(
                font=dict(color="#0F172A", size=12),
                title=dict(font=dict(color="#0F172A", size=12)),
            ),
        )
        fig.update_xaxes(
            title_font=dict(color="#0F172A", size=13),
            tickfont=dict(color="#334155", size=11),
            gridcolor="#E2E8F0",
            linecolor="#CBD5E1",
        )
        fig.update_yaxes(
            title_font=dict(color="#0F172A", size=13),
            tickfont=dict(color="#334155", size=11),
            gridcolor="#E2E8F0",
            linecolor="#CBD5E1",
        )


def get_folium_tiles() -> str:
    """Return Folium basemap tile layer name according to current theme."""
    return "CartoDB dark_matter" if st.session_state.get("theme") == "dark" else "CartoDB positron"


def get_status_pill_colors() -> dict[str, str]:
    """Theme-aware replacement for Page 6's audit status pill colors."""
    if st.session_state.get("theme") == "dark":
        return {
            "healthy_bg": "#1b5e20",
            "healthy_text": "#c8e6c9",
            "degenerate_bg": "#b71c1c",
            "degenerate_text": "#ffcdd2",
        }
    return {
        "healthy_bg": "#c8e6c9",
        "healthy_text": "#1b5e20",
        "degenerate_bg": "#ffcdd2",
        "degenerate_text": "#b71c1c",
    }


def get_top10_highlight_colors() -> dict[str, str]:
    """Theme-aware replacement for Pages 1-3's Top-10 row highlight colors."""
    if st.session_state.get("theme") == "dark":
        return {"bg": "#1b5e20", "text": "#ffffff"}
    return {"bg": "#a5d6a7", "text": "#1b5e20"}
