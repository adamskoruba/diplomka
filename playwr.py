from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()

    page.goto("https://skoruba.sk")
    input("Press ENTER to quit...")

    browser.close()