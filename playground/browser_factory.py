from selenium import webdriver
from enum import Enum
from magic import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service

CHROME_FOR_TESTING_PATH = r"C:\Users\adams\Downloads\chrome-win64\chrome-win64\chrome.exe"
CHROME_BETA_PATH = r"C:\Program Files\Google\Chrome Beta\Application\chrome.exe"
CHROMEDRIVER_FOR_TESTING_PATH = r"C:\Users\adams\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"


# driver = uc.Chrome(browser_executable_path=CHROME_FOR_TESTING_PATH,
#                    driver_executable_path=CHROMEDRIVER_FOR_TESTING_PATH)

class BrowserType(Enum):
    DEFAULT_SELENIUM = "default_selenium"

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