import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ChromeSelenium:
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('disable-gpu')
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(executable_path='chromedriver', options=options)

    # driver.implicitly_wait(20)

    def __init__(self):
        pass

    def findElement(self, coin):
        try:
            for i in range(40):
                try:
                    self.driver.get(url=coin.url)
                    time.sleep(1)

                    if "opensea" in coin.url:
                        element = self.driver.find_elements(by=By.XPATH, value=coin.xpath2)
                        content_name = element[0].text
                        print("content name", content_name, end=" - ")
                        if "Offer".casefold() in content_name.casefold():
                            print("caught offer case", end=" - ")
                            return -1

                    element = self.driver.find_elements(by=By.XPATH, value=coin.xpath)
                    element = element[0].text
                except Exception as e:
                    #print(str(e), end=" - ")
                    continue
                else:
                    break

            if re.search("[-]?\d*.\d*\%", element):
                result = re.split("[-]?\d*.\d*\%", element)[0]
            elif re.search("\d*.\d*\r\n", element):
                result = element[0].replace("\r\n", "")
            elif re.search("\d*.\d*\n", element):
                result = re.split("\n", element)[0]
            else:
                result = element

            result = result.replace(",", "")
            result = result.replace("$", "")
            result = result.replace("+", "")
            result = result.replace("-", "")
        except Exception as e:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            #print(message)
            result = -1
        return result
