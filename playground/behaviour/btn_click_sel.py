import time

from selenium.webdriver.common.by import By
from selenium import webdriver

driver = webdriver.Chrome()
driver.get("http://localhost:8000/mouse")

time.sleep(2)
btn = driver.find_element(By.ID, "btn-click-me")
btn.click()

input("Nech to nevypne..")