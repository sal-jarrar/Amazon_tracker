import time
from datetime import datetime
import json
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from amazon_config import(
    BASE_URL,
    CURRENCY,
    FILTERS,
    NAME,
    DIR,
    get_chrom_web_driver,
    get_web_driver_option,
    set_browser_as_incognito,
    set_ignore_certificate_error
)


class GenerateReport():
    def __init__(self, file, filters, base_link, currency, data):
        self.file = file
        self.filters = filters
        self.base_link = base_link
        self.currency = currency
        self.data = data

        report = {
            "title": self.file,
            "date": self.get_date(),
            "best_item": self.get_best(),
            "currency": self.currency,
            "url": self.base_link,
            "products": self.data
        }
        print("Creating report....")

        with open(f"{DIR}/{file}.json", "w") as f:
            json.dump(report, f)
        print("Done....")

    def get_date(self):
        now = datetime.now()
        return now.strftime("%m/%d/%Y, %H:%M:%S")

    def get_best(self):
        try:
            return sorted(self.data, key=lambda x: x["price"])[0]
        except Exception as e:
            print(e)
            return None


class AmazonAPI():
    def __init__(self, search_term, filters, base_url, currency):
        self.search_term = search_term
        self.base_url = base_url
        self.currency = currency
        option = get_web_driver_option()
        self.drive = get_chrom_web_driver(option)
        set_browser_as_incognito(option)
        set_ignore_certificate_error(option)
        self.price_filter = f"&rh=p_36%3A{filters['min']}00-{filters['max']}00"

    def run(self):
        print("starting script..")
        print(f'Looking for {self.search_term} products....')
        links = self.get_product_links()
        time.sleep(3)
        if not links:
            print('stopped script.')
            return
        print(f"Got {len(links)} links to products")
        print("Getting info about prouducts....")
        product = self. get_product_info(links)
        time.sleep(3)
        return product
        self.drive.quit()

    def get_product_links(self):
        self.drive.get(self.base_url)
        element = self.drive.find_element_by_id("twotabsearchtextbox")
        element.send_keys(self.search_term)
        element.send_keys(Keys.ENTER)
        time.sleep(2)
        self.drive.get(f"{self.drive.current_url}{self.price_filter}")
        time.sleep(2)
        results_list = self.drive.find_elements_by_class_name(
            "s-result-list")

        links = []
        try:
            results = results_list[0].find_elements_by_xpath(
                "//div/span/div/div/div[2]/div[2]/div/div[1]/div/div/div[1]/h2/a")
            links = [link.get_attribute("href") for link in results]
        except Exception as e:
            print("did not get any product....")
            print(e)
        return links

    def get_product_info(self, links):

        clear_links = self.get_clear_links(links)
        products = []
        for link in clear_links:
            product = self.get_single_product_info(link)
            if product:
                products.append(product)
        return products

    def get_single_product_info(self, link):
        print(f"Product ID: {link}")
        product_short_url = self.short_url(link)
        self.drive.get(f"{product_short_url}?language=en_GB")
        time.sleep(3)
        title = self.get_product_title()
        seller = self.get_seller()
        price = self.get_price()
        if title and seller and price:
            product_info = {
                "title": title,
                "seller": seller,
                "price": price,
                'url': product_short_url
            }
            return product_info
        return None

    def get_price(self):
        price = None
        try:
            price = self.drive.find_element_by_id("priceblock_ourprice").text
            price = self.convert_price(price)
        except NoSuchElementException:
            try:
                ava = self.drive.find_element_by_id("availability").text
                if "Available" in ava:
                    price = self.drive.find_element_by_class_name(
                        "olp-padding-right")
                    price = price[price.find(self.currency):]
                    price = price.convert_price(price)
            except Exception as e:
                print(e)
                print(f"Can't get price of product {self.drive.current_url}")
                return None
        except Exception as e:
            print(e)
            print("Can't get price of product .")
        return price

    def get_product_title(self):
        try:
            title = self.drive.find_element_by_id("productTitle").text
            return(title)
        except Exception as e:
            print("did not get any product....")
            print(e)
            return None

    def get_seller(self):
        try:
            seller = self.drive.find_element_by_id("bylineInfo").text
            return(seller)

        except Exception as e:
            print("did not get any product....")
            print(e)
            return None

    def short_url(self, link):
        return self.base_url + "/dp/"+link

    def get_clear_links(self, links):
        return [self.get_clear_link(link) for link in links]

    def get_clear_link(self, product_link):
        return product_link[product_link.find('/dp/')+4:product_link.find("/ref")]

    def convert_price(self, price):
        price = price.split(self.currency)[1]
        try:
            price = price.split("\n")[0]+"."+price.split("\n")[1]
        except:
            Exception()

        try:
            price = price.split("\n")[0]+","+price.split("\n")[1]
        except:
            Exception()

        return float(price)


if __name__ == "__main__":
    print("OKKK")


amazon = AmazonAPI(NAME, FILTERS, BASE_URL, CURRENCY)
data = amazon.run()
GenerateReport(NAME, FILTERS, BASE_URL, CURRENCY, data)
