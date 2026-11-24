from curl_cffi import requests


response = requests.get("https://skoruba.sk/dp", impersonate="chrome")
print(response.status_code)
print(response.text)