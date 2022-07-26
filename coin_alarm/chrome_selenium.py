import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ChromeSelenium:
    # options = webdriver.ChromeOptions()
    # #options.add_argument('headless')
    # options.add_argument('disable-gpu')
    # options.add_experimental_option('useAutomationExtension', False)
    # options.add_argument('--disable-browser-side-navigation')
    # options.add_argument('--disable-blink-features=AutomationControlled')
    # driver = webdriver.Chrome(executable_path='chromedriver', options=options)
    # driver.implicitly_wait(10)

    def __init__(self):
        options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        options.add_argument('disable-gpu')
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-browser-side-navigation')
        options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(executable_path='chromedriver', options=options)
        self.driver.implicitly_wait(10)
        self.driver.set_page_load_timeout(10)

    def findElement(self, coin):
        try:
            for i in range(40):
                try:

                    self.driver.get(url=coin.url)
                    print("driver.get")

                    # if "opensea" in coin.url:
                    #     element = self.driver.find_elements(by=by.xpath, value=coin.xpath2)
                    #     content_name = element[0].text
                    #     print("content name", content_name, end=" - ")
                    #     if "offer".casefold() in content_name.casefold():
                    #         print("caught offer case", end=" - ")
                    #         return -1

                    element = self.driver.find_elements(by=By.XPATH, value=coin.xpath)
                    element = element[0].text
                except Exception as e:
                    print(str(e))
                    continue
                else:
                    break

            if re.search("\d*.\d*\r\n", element):
                result = element[0].replace("\r\n", "")
            elif re.search("\d*.\d*\n", element):
                result = re.split("\n", element)[0]
            else:
                result = element

            result = result.replace("%", "")
            result = result.replace(",", "")
            result = result.replace("$", "")
            result = result.replace("+", "")
            #result = result.replace("-", "")
        except Exception as e:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message)
            result = -1
        return result
