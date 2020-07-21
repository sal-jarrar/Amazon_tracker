from selenium import webdriver

BASE_URL = "https://www.amazon.de/"

DIR = 'reports'
NAME = 'ps4'
MAX_PRICE = "700"
MIN_PRICE = "300"
CURRENCY = "€"
FILTERS = {
    "min": MIN_PRICE,
    'max': MAX_PRICE,
}


def get_chrom_web_driver(option):
    return webdriver.Chrome("./chromedriver", chrome_options=option)


def get_web_driver_option():
    return webdriver.ChromeOptions()


def set_ignore_certificate_error(option):
    option.add_argument('--ignore-certificate-errors')


def set_browser_as_incognito(option):
    option.add_argument("--incognito")
