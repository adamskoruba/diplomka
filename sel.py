from selenium import webdriver

COLOSSEO = "https://ticketing.colosseo.it/en/"
ALZA = "https://alza.sk"
CLOUDFLARE = "https://www.cloudflare.com/"
TICKETMASTER = "https://www.ticketmaster.com/"
CHATGPT = "https://www.chatgpt.com/"

driver = webdriver.Chrome()
# driver.execute_cdp_cmd("Network.enable", {})
# driver.execute_cdp_cmd(
#                     "Page.addScriptToEvaluateOnNewDocument",
#                     {
#                         "source": """
#
#                            Object.defineProperty(window, "navigator", {
#                                 Object.defineProperty(window, "navigator", {
#                                   value: new Proxy(navigator, {
#                                     has: (target, key) => (key === "webdriver" ? false : key in target),
#                                     get: (target, key) =>
#                                       key === "webdriver"
#                                         ? false
#                                         : typeof target[key] === "function"
#                                         ? target[key].bind(target)
#                                         : target[key],
#                                   }),
#                                 });
#                     """
#                     },
#                 )

driver.get(CHATGPT)
input("Press ENTER to quit...")
driver.quit()