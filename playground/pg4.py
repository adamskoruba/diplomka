from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        executable_path=r"C:\src\chromium\src\out\Default\chrome.exe"
    )

    context = browser.new_context(
        ignore_https_errors=True
    )

    page = context.new_page()

    page.goto("https://waf.skoruba.sk", wait_until="load")

    page.wait_for_timeout(500000)

    browser.close()