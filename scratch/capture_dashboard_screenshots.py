"""Automated high-resolution screenshot capture for Streamlit Showcase Dashboard."""

import time
from pathlib import Path
from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS_DIR = REPO_ROOT / "assets" / "Screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Define target pages and output file names
PAGES = [
    {"name": "00_Home_Overview.png", "title": "Home", "wait_extra": 2},
    {"name": "01_Site_Map.png", "title": "1. Site Map", "wait_extra": 4},
    {"name": "02_MCDM_Rankings.png", "title": "2. MCDM Rankings", "wait_extra": 3},
    {"name": "03_Whatif_Weight_Explorer.png", "title": "3. What-If Explorer", "wait_extra": 3},
    {"name": "04_Demand_and_SHAP.png", "title": "4. Demand & SHAP", "wait_extra": 3},
    {"name": "05_Sensitivity_Analysis.png", "title": "5. Sensitivity Analysis", "wait_extra": 3},
    {"name": "06_Data_Quality_Audit.png", "title": "6. Data Quality Audit", "wait_extra": 3},
    {"name": "07_Project_Journey.png", "title": "7. Project Journey", "wait_extra": 3},
]


def capture_all_pages():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Create context with 1920x1080 viewport and 2x device scale for crisp 4K-quality screenshots
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,
        )
        page = context.new_page()

        print("Navigating to local Streamlit dashboard at http://localhost:8501...")
        page.goto("http://localhost:8501", wait_until="networkidle", timeout=60000)
        time.sleep(3)

        for item in PAGES:
            filename = item["name"]
            title = item["title"]
            out_path = SCREENSHOTS_DIR / filename

            print(f"\n[Capturing] {title} -> {filename}...")

            # Locate sidebar button / link matching page title
            try:
                # Streamlit navigation sidebar items
                nav_item = page.get_by_text(title, exact=False).first
                if nav_item.is_visible():
                    nav_item.click()
                    time.sleep(1)
            except Exception as e:
                print(f"Could not click nav item {title}: {e}")

            # Wait for Streamlit to finish rendering
            time.sleep(item["wait_extra"])
            page.wait_for_load_state("networkidle")

            # Capture full page screenshot
            page.screenshot(path=str(out_path), full_page=True)
            print(f"Saved: {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")

        browser.close()
        print("\nAll dashboard screenshots captured successfully!")


if __name__ == "__main__":
    capture_all_pages()
