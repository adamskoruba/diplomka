
import ssl
import requests
import urllib3
import curl_cffi
from curl_cffi import Curl
from curl_cffi import requests as curl_requests

URL = "https://steamkody.sk"

print("=" * 65)
print("1. REQUESTS / PYTHON SSL")
print("=" * 65)

print("Python SSL:", ssl.OPENSSL_VERSION)
print("requests:", requests.__version__)
print("urllib3:", urllib3.__version__)

try:
    with requests.get(URL, timeout=15, stream=True) as r:
        print("HTTP status:", r.status_code)
        print("HTTP version:", r.raw.version)

        conn = getattr(r.raw, "connection", None)
        sock = getattr(conn, "sock", None)

        if sock:
            print("Negotiated TLS:", sock.version())
            print("Cipher:", sock.cipher())
            print("Peer certificate:", sock.getpeercert())
        else:
            print("TLS socket nie je dostupný cez urllib3 response.")

except Exception as e:
    print(type(e).__name__ + ":", e)


print("\n" + "=" * 65)
print("2. CURL_CFFI / LIBCURL TLS BACKEND")
print("=" * 65)

print("curl_cffi:", curl_cffi.__version__)

try:
    curl = Curl()
    print("libcurl / TLS backend:")
    print(curl.version())
    curl.close()
except Exception as e:
    print("Version error:", repr(e))

try:
    r = curl_requests.get(
        URL,
        impersonate="chrome",
        timeout=15,
    )

    print("HTTP status:", r.status_code)
    print("HTTP version:", r.http_version)
    print("Cookies:", r.cookies.get_dict())

except Exception as e:
    print(type(e).__name__ + ":", e)