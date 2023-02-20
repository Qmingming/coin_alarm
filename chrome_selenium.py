from datetime import datetime
import logging
import re
import time

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ChromeSelenium:
    #options = webdriver.ChromeOptions()
    #options.add_argument('headless')
    # options.add_argument('disable-gpu')
    # options.add_experimental_option('useAutomationExtension', False)
    # options.add_argument('--disable-browser-side-navigation')
    # options.add_argument('--disable-blink-features=AutomationControlled')
    # driver = webdriver.Chrome(executable_path='chromedriver', options=options)
    # driver.implicitly_wait(10)

    def __init__(self):
        cap = DesiredCapabilities().FIREFOX
        cap["marionette"] = True
        options = webdriver.FirefoxOptions()
        #options.add_argument('--headless')
        #options.add_argument('disable-gpu')
        #options.add_experimental_option('useAutomationExtension', False)
        #options.add_argument('--disable-browser-side-navigation')
        #options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Firefox(executable_path='geckodriver.exe', options=options, capabilities=cap)
        self.driver.maximize_window()
        #self.driver.implicitly_wait(4)
        #self.driver.set_page_load_timeout(10)

    def findElement(self, coin):
        try:
            for i in range(2):
                try:
                    self.driver.get(url=coin.url)
                    #logging.info("driver.get")

                    # if "opensea" in coin.url:
                    #     element = self.driver.find_elements(by=by.xpath, value=coin.xpath2)
                    #     content_name = element[0].text
                    #     print("content name", content_name, end=" - ")
                    #     if "offer".casefold() in content_name.casefold():
                    #         print("caught offer case", end=" - ")
                    #         return -1
                    time.sleep(2)
                    #element = WebDriverWait(self.driver, 10).until(
                    #    EC.visibility_of_element_located((By.XPATH, coin.xpath))
                    #)
                    element = self.driver.find_elements(by=By.XPATH, value=coin.xpath)

                    current_time = datetime.now().strftime("%H:%M:%S")
                    #print(current_time, element)
                except Exception as err:
                    print(str(err))
                    continue
                else:
                    break

            if len(element) == 0:
                return -1
            else:
                element = element[0].text
                print(element)

            if re.search("\d*.\d*\r\n", element):
                result = element[0].replace("\r\n", "")
            elif re.search("\d*.\d*\n", element):
                result = re.split("\n", element)[0]
            else:
                result = element

            result = result.replace("ETH", "")
            result = result.replace("WETH", "")
            result = result.replace("WKLAY", "")
            result = result.replace("KLAY", "")
            result = result.replace("%", "")
            result = result.replace(",", "")
            result = result.replace("$", "")
            result = result.replace("+", "")
            #result = result.replace("-", "")
        except Exception as err:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(err).__name__, err.args)
            print(message)
            result = -1
        return result
