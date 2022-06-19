import re
from datetime import time
from decimal import Decimal

import selenium
from selenium import webdriver
from selenium.webdriver import ActionChains

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait


class ChromeSelenium:
    options = webdriver.ChromeOptions()
    #options.add_argument('headless')
    options.add_argument('disable-gpu')
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(executable_path='chromedriver', options=options)
    #driver.implicitly_wait(20)

    def __init__(self):
        pass

    def findElement(self, url, xpath):
        try:
            #driver = webdriver.Chrome(executable_path='chromedriver', options=self.options)
            self.driver.get(url=url)
            self.driver.implicitly_wait(10)
            element = self.driver.find_elements(by=By.XPATH, value=xpath)
            #element = WebDriverWait(driver, 20).until(
            #    EC.presence_of_element_located((By.XPATH, xpath))
            #).text

            #element = elements.text

            if re.search("[-]?\d*.\d*\%", element[0].text):
                result = re.split("[-]?\d*.\d*\%", element[0].text)[0]
            elif re.search("\d*.\d*\r\n", element[0].text):
                result = element[0].replace("\r\n", "")
            elif re.search("\d*.\d*\n", element[0].text):
                result = re.split("\n", element[0].text)[0]
            else:
                result = element[0].text

            result = result.replace(",", "")
            result = result.replace("$", "")
            result = result.replace("+", "")
            result = result.replace("-", "")

            # print(result)
            # print(Decimal(result))
        except Exception as e:
            print(e)
            result = -1

        return result

# driver = ChromeSelenium()
# driver.findElement(
# "https://dexata.kr/?tokenA=0x0000000000000000000000000000000000000000&tokenB=0xcee8faf64bb97a73bb51e115aa89c17ffa8dd167",
# "/html/body/app-root/route-index/div/div/trading-view-chart/div[2]/div[1]/div[1]/div[2]")
