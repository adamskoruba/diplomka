from magic import undetected_chromedriver as uc

driver = uc.Chrome()

CHATGPT = "https://www.chatgpt.com/"

driver.get(CHATGPT)
input("Press ENTER to quit...")
driver.quit()