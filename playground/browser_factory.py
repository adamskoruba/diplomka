import subprocess
import time

import requests

from selenium import webdriver
from enum import Enum

from selenium.webdriver.chrome.options import Options

from magic import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service

CHROME_FOR_TESTING_PATH = r"C:\Users\adams\Downloads\chrome-win64\chrome-win64\chrome.exe"
CHROME_BETA_PATH = r"C:\Program Files\Google\Chrome Beta\Application\chrome.exe"
CHROMEDRIVER_FOR_TESTING_PATH = r"C:\Users\adams\Downloads\chromedriver-win32\chromedriver-win32\chromedriver.exe"


# driver = uc.Chrome(browser_executable_path=CHROME_FOR_TESTING_PATH,
#                    driver_executable_path=CHROMEDRIVER_FOR_TESTING_PATH)

class BrowserType(Enum):
    DEFAULT_SELENIUM = "default_selenium"
    UNDETECTED_CHROMEDRIVER = "undetected_chromedriver"
    CUSTOM_SELENIUM = "custom_selenium"
    CHROME_SUBPROCESS = "chrome_subprocess"
    CUSTOM_CHROMIUM = "custom_chrome"

class BrowserFactory:
    _registry = {}

    @classmethod
    def register(cls, browser_type: BrowserType):
        def wrapper(func):
            cls._registry[browser_type] = func
            return func
        return wrapper

    @classmethod
    def create(cls, browser_type: BrowserType):
        try:
            return cls._registry[browser_type]()
        except KeyError:
            raise ValueError(f"Unsupported browser: {browser_type}")


@BrowserFactory.register(BrowserType.DEFAULT_SELENIUM)
def create_default_selenium():
    options = webdriver.ChromeOptions()
    options.binary_location = CHROME_BETA_PATH
    service = Service(CHROMEDRIVER_FOR_TESTING_PATH)

    driver = webdriver.Chrome(options=options, service=service)
    return driver

@BrowserFactory.register(BrowserType.CUSTOM_SELENIUM)
def create_custom_selenium():
    options = Options()



    # flags = [
    #     "--lang=sk-SK",
    #     "--no-default-browser-check",
    #     "--no-first-run",
    #     "--no-sandbox",
    #     "--test-type",
    #     "--window-size=1920,1080",
    #     "--start-maximized",
    #     "--log-level=0",
    #     "--flag-switches-begin",
    #     "--flag-switches-end",
    # ]
    #
    # options = Options()
    # for flag in flags:
    #     options.add_argument(flag)
    # print(options)
    options.binary_location = CHROME_BETA_PATH
    service = Service(CHROMEDRIVER_FOR_TESTING_PATH)

    driver = webdriver.Chrome(options=options, service=service)
    return driver

@BrowserFactory.register(BrowserType.UNDETECTED_CHROMEDRIVER)
def create_undetected_chromedriver():
    driver = uc.Chrome(browser_executable_path=CHROME_BETA_PATH)
    return driver

@BrowserFactory.register(BrowserType.CHROME_SUBPROCESS)
def create_chrome_subprocess():
    subprocess.Popen([
        CHROME_FOR_TESTING_PATH,
        "--remote-debugging-port=9222",
    ])
    options = Options()
    options.debugger_address = "127.0.0.1:9222"
    options.binary_location = CHROME_FOR_TESTING_PATH

    time.sleep(5)

    driver = webdriver.Chrome(
        service=Service(executable_path=CHROMEDRIVER_FOR_TESTING_PATH,),
        options=options
    )
    return driver


@BrowserFactory.register(BrowserType.CUSTOM_CHROMIUM)
def create_custom_chromium():
    chromium_path = r"C:\src\chromium\src\out\Default\chrome.exe"
    chromedriver_path = r"C:\src\chromium\src\out\Default\chromedriver.exe"

    options = Options()
    options.binary_location = chromium_path

    service = Service(executable_path=chromedriver_path)

    driver = webdriver.Chrome(options=options, service=service)
    return driver

"""@BrowserFactory.register(BrowserType.?)
def create_default_selenium():
    driver = uc.Chrome(browser_executable_path=CHROME_FOR_TESTING_PATH,
    driver_executable_path=CHROMEDRIVER_FOR_TESTING_PATH)
    return driver"""