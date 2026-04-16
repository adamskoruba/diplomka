import io
import re

path = r"C:\Users\adams\AppData\Roaming\undetected_chromedriver\undetected_chromedriver.exe"


with io.open(path, "rb") as f:
    content = f.read()

print(content.decode(errors="ignore"))