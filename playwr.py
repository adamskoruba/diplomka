from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto("https://dp.skoruba.sk/")
    input("Press ENTER to quit...")

    browser.close()