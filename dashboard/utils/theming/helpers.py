"""Theme-conditional visualization and styling helper functions."""

import streamlit as st


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
            coloraxis_colorbar=dict(
                title=dict(font=dict(color="#FAFAFA", size=13)),
                tickfont=dict(color="#E6EDF3", size=11),
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
            coloraxis_colorbar=dict(
                title=dict(font=dict(color="#0F172A", size=13)),
                tickfont=dict(color="#0F172A", size=11),
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
        return {
            "bg": "#1b5e20",
            "text": "#ffffff",
            "normal_bg": "#161B22",
            "normal_text": "#FAFAFA",
        }
    return {
        "bg": "#a5d6a7",
        "text": "#1b5e20",
        "normal_bg": "#FFFFFF",
        "normal_text": "#1E293B",
    }
