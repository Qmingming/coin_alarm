import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ChromeSelenium:
    options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    options.add_argument('disable-gpu')
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(executable_path='chromedriver', options=options)

    # driver.implicitly_wait(20)

    def __init__(self):
        pass

    def findElement(self, url, xpath):
        try:
            # driver = webdriver.Chrome(executable_path='chromedriver', options=self.options)
            for i in range(40):
                try:
                    self.driver.get(url=url)
                    time.sleep(0.5)
                    element = self.driver.find_elements(by=By.XPATH, value=xpath)
                    element = element[0].text
                except Exception as e:
                    print("An exception of {0} type occurred".format(type(e)))
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

            # print(result)
            # print(Decimal(result))
        except Exception as e:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message)
            result = -1
        return result
