import ex_selenium
from ex_selenium import webdriver
from ex_selenium.webdriver import ActionChains

from ex_selenium.webdriver.common.keys import Keys
from ex_selenium.webdriver.common.by import By

from ex_selenium.webdriver.support import expected_conditions as EC
from ex_selenium.webdriver.support.ui import Select
from ex_selenium.webdriver.support.ui import WebDriverWait

URL = "https://opensea.io/collection/syltare-dawn-of-east?search[sortAscending]=true&search[sortBy]=PRICE&search[toggles][0]=BUY_NOW"

driver = webdriver.Chrome(executable_path='chromedriver')
driver.get(url=URL)
#elements = driver.find_elements_by_xpath('//*[@id="main"]/div/div/div[5]/div/div[3]/div[3]/div[3]/div[4]/div[2]/div/div/div[1]/div/article/a/div[2]/div/div[2]/div[1]/div/div[2]')
elements = driver.find_elements(by=By.Xpath, value='//*[@id="main"]/div/div/div[5]/div/div[3]/div[3]/div[3]/div[4]/div[2]/div/div/div[1]/div/article/a/div[2]/div/div[2]/div[1]/div/div[2]')
for element in elements:
    print(element.text)
print(driver.current_url)
