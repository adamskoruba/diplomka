from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://nike.sk")
input("Press ENTER to quit...")
driver.quit()