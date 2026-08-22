"""Smoke tests for Streamlit dashboard pages using streamlit.testing.v1.AppTest.

Ensures that dashboard/app.py and all multi-page scripts in dashboard/pages/
render completely without unhandled exceptions or deprecated API crashes.
"""

from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

REPO_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = REPO_ROOT / "dashboard"
PAGES_DIR = DASHBOARD_DIR / "pages"

PAGES = [
    DASHBOARD_DIR / "app.py",
    PAGES_DIR / "1_Site_Map.py",
    PAGES_DIR / "2_MCDM_Rankings.py",
    PAGES_DIR / "3_Whatif_Weight_Explorer.py",
    PAGES_DIR / "4_Demand_and_SHAP.py",
    PAGES_DIR / "5_Sensitivity_Analysis.py",
    PAGES_DIR / "6_Data_Quality_Audit.py",
    PAGES_DIR / "7_Project_Journey.py",
]


@pytest.mark.parametrize("page_path", PAGES, ids=[p.name for p in PAGES])
def test_page_renders_without_exception(page_path: Path):
    """Verify each dashboard page runs to completion with zero uncaught exceptions."""
    assert page_path.exists(), f"Page file does not exist: {page_path}"
    
    # Run the AppTest directly against the page file
    at = AppTest.from_file(str(page_path), default_timeout=30)
    at.run()
    
    # Assert zero exceptions occurred during rendering
    if len(at.exception) > 0:
        error_msgs = [f"Exception {i+1}: {e.value}" for i, e in enumerate(at.exception)]
        pytest.fail(f"Page {page_path.name} failed with {len(at.exception)} exception(s):\n" + "\n".join(error_msgs))
    
    assert len(at.exception) == 0


def test_smoke_home_overview_elements():
    """Verify specific key elements on the Home Overview page."""
    at = AppTest.from_file(str(DASHBOARD_DIR / "app.py"), default_timeout=30)
    at.run()
    
    assert len(at.exception) == 0
    # Confirm metrics rendered
    assert len(at.metric) >= 4
    # Confirm subheaders exist
    assert len(at.subheader) >= 3


def test_smoke_data_quality_audit_table_rendered():
    """Verify Page 6 Data Quality Audit renders the audit table cleanly."""
    at = AppTest.from_file(str(PAGES_DIR / "6_Data_Quality_Audit.py"), default_timeout=30)
    at.run()
    
    assert len(at.exception) == 0
    # Confirm table or dataframe rendered without Pandas Styler exceptions
    assert len(at.table) >= 1 or len(at.dataframe) >= 1


def test_theme_toggle_interaction_and_switch():
    """Verify clicking the sidebar theme toggle safely mutates state and updates UI without errors."""
    at = AppTest.from_file(str(DASHBOARD_DIR / "app.py"), default_timeout=30)
    at.run()
    
    assert len(at.exception) == 0
    assert at.session_state["theme"] == "light"
    
    toggle_btn = at.button(key="theme_toggle_btn")
    assert toggle_btn is not None
    assert toggle_btn.label == "Dark Mode"
    
    # Simulate first click: Light -> Dark
    toggle_btn.click().run()
    assert len(at.exception) == 0
    assert at.session_state["theme"] == "dark"
    assert at.button(key="theme_toggle_btn").label == "Light Mode"
    
    # Simulate second click: Dark -> Light
    at.button(key="theme_toggle_btn").click().run()
    assert len(at.exception) == 0
    assert at.session_state["theme"] == "light"
    assert at.button(key="theme_toggle_btn").label == "Dark Mode"

