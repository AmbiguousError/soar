
import time
from playwright.sync_api import sync_playwright

def run_verification(playwright):
    # Emulate an iPhone 11
    iphone_11 = playwright.devices['iPhone 11']
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(**iphone_11)
    page = context.new_page()

    try:
        page.goto("http://localhost:8000")
        page.wait_for_selector("canvas", state="attached")
        time.sleep(1)

        # --- Main Menu (Tap to start) ---
        page.tap("canvas", position={"x": 200, "y": 300})
        time.sleep(1)

        # --- Mode Selection (Tap to select Dogfight) ---
        page.tap("canvas", position={"x": 200, "y": 300}) # Approximate position for Dogfight
        time.sleep(2)

        # --- In-Game Screenshot ---
        page.screenshot(path="jules-scratch/verification/02_mobile_view_fix.png")

    finally:
        browser.close()

with sync_playwright() as playwright:
    run_verification(playwright)
