import time

from browser_factory import BrowserFactory, BrowserType
from js.utils import load_js

CHATGPT = "https://www.chatgpt.com/"
DP = "https://dp.skoruba.sk/"
CHROME_VERSION="chrome://version"

browser = BrowserFactory.create(BrowserType.CUSTOM_CHROME)

#browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": load_js("touched_navigator.js")})
#browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": load_js("patch_webdriver.js")})

print('xd')
browser.get(DP)
input("Press ENTER to quit...")
browser.quit()
