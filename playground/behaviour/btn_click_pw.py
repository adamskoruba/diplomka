from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    context = browser.new_context(
        ignore_https_errors=True
    )

    page = context.new_page()

    page.goto("http://localhost:8000/mouse", wait_until="load")
    time.sleep(2)

    page.click("#btn-click-me")

    page.wait_for_timeout(500000)

    browser.close()