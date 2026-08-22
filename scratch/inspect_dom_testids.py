import time
import subprocess
from playwright.sync_api import sync_playwright

proc = subprocess.Popen([
    r".\.venv\Scripts\streamlit.exe", "run", "dashboard/app.py",
    "--server.port", "8505", "--server.headless", "true"
])
time.sleep(4)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8505", wait_until="networkidle", timeout=30000)
        time.sleep(2)
        
        elements = page.query_selector_all("[data-testid]")
        testids = set()
        for el in elements:
            tid = el.get_attribute("data-testid")
            if tid:
                testids.add(tid)
        
        print("Unique data-testids found:")
        for t in sorted(list(testids)):
            print(f"  - {t}")
        
        stapp = page.query_selector(".stApp")
        print(".stApp exists:", stapp is not None)
        sidebar = page.query_selector('[data-testid="stSidebar"]')
        print('[data-testid="stSidebar"] exists:', sidebar is not None)
        metric = page.query_selector('[data-testid="stMetric"]')
        print('[data-testid="stMetric"] exists:', metric is not None)
        stdataframe = page.query_selector('[data-testid="stDataFrame"]')
        print('[data-testid="stDataFrame"] exists:', stdataframe is not None)
        
        browser.close()
finally:
    proc.terminate()
