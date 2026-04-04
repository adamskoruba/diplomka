from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://ticketing.colosseo.it/en/")
input("Press ENTER to quit...")
driver.quit()