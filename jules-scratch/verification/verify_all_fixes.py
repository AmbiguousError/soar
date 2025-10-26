
import time
from playwright.sync_api import sync_playwright

def run_verification(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    try:
        page.goto("http://localhost:8000")
        page.wait_for_selector("canvas", state="attached")
        time.sleep(1)

        # --- 1. Main Menu & Glider Sprite ---
        page.screenshot(path="jules-scratch/verification/01_fix_main_menu_final.png")
        page.keyboard.press("Enter")
        time.sleep(1)

        # --- 2. Free Fly: Altitude Loss & Thermals ---
        page.keyboard.press("Enter") # Select Free Fly
        time.sleep(3)
        page.screenshot(path="jules-scratch/verification/02_fix_free_fly_final.png")
        page.keyboard.press("Escape")
        time.sleep(1)

        # --- 3. Race: Gate Trigger ---
        page.keyboard.press("ArrowDown") # Select Race
        page.keyboard.press("Enter")
        time.sleep(1)
        page.keyboard.down("ArrowUp") # Fly forward
        time.sleep(2)
        page.keyboard.up("ArrowUp")
        page.screenshot(path="jules-scratch/verification/03_fix_race_gate_final.png")

    finally:
        browser.close()

with sync_playwright() as playwright:
    run_verification(playwright)
