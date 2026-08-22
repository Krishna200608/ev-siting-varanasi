"""CSS asset loader for Light and Dark dashboard themes."""

from pathlib import Path
import streamlit as st

_ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets"


def _load_css(filename: str) -> str:
    """Read a raw CSS file from dashboard/assets and wrap it in a <style> tag."""
    css_path = _ASSETS_DIR / filename
    return f"<style>\n{css_path.read_text(encoding='utf-8')}\n</style>"


def inject_css(theme: str) -> None:
    """Inject raw stylesheet into Streamlit markdown container based on active theme."""
    filename = "theme_dark.css" if theme == "dark" else "theme_light.css"
    st.markdown(_load_css(filename), unsafe_allow_html=True)
