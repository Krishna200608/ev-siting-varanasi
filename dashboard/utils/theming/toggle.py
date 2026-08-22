"""Theme toggle and persistence logic for the dashboard."""

import streamlit as st
from .css_loader import inject_css


def inject_theme_and_toggle() -> None:
    """Inject theme CSS and render the sidebar theme toggle button.
    
    Persists theme across browser refreshes and page navigation using st.query_params.
    Call at the top of every page (app.py + all files in pages/).
    """
    query_theme = st.query_params.get("theme")
    if "theme" not in st.session_state:
        if query_theme in ("light", "dark"):
            st.session_state.theme = query_theme
        else:
            st.session_state.theme = "light"
    
    # Keep query_params synchronized for URL bookmarking and refresh persistence
    if st.query_params.get("theme") != st.session_state.theme:
        st.query_params["theme"] = st.session_state.theme

    inject_css(st.session_state.theme)

    with st.sidebar:
        is_light = st.session_state.theme == "light"
        icon = ":material/dark_mode:" if is_light else ":material/light_mode:"
        label = "Dark Mode" if is_light else "Light Mode"
        if st.button(label, icon=icon, key="theme_toggle_btn", width="stretch"):
            new_theme = "dark" if is_light else "light"
            st.session_state.theme = new_theme
            st.query_params["theme"] = new_theme
            st.rerun()
