from browser_factory import BrowserFactory, BrowserType
from js.utils import load_js

CHATGPT = "https://www.chatgpt.com/"
DP = "https://dp.skoruba.sk/"

browser = BrowserFactory.create(BrowserType.DEFAULT_SELENIUM)

browser.execute_cdp_cmd(
    "Page.addScriptToEvaluateOnNewDocument",
    {"source": load_js("webdriver.js")}
)

browser.get(DP)
input("Press ENTER to quit...")
browser.quit()
