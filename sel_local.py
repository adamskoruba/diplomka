from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://dp.skoruba.sk")
input("Press ENTER to quit...")
driver.quit()