import instaloader

import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome, Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def read_file(path):
    with open(path, 'r') as arq:
        lista = arq.readlines()
    return lista

def yt_scrap(url, n):
    data=[]
    options = Options()
    options.add_argument('--headless')
    with Chrome('chromedriver', options=options) as driver:
        wait = WebDriverWait(driver,15)
        driver.get(url)

        for _ in range(n): 
            wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.END)
            time.sleep(15)

        for comment in wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#content"))):
            data.append(comment.text)
    return data[3:]


def insta_scrap(url, n):
    data, i = [], 0
    options = Options()
    options.add_argument('--headless')
    with Chrome('chromedriver', options=options) as driver:
        wait = WebDriverWait(driver,15)
        driver.get(url)

        while n>i:
            try:
                driver.find_element_by_class_name('dCJp8').click()
            except NoSuchElementException:
                break
            time.sleep(15)
            i =+ 1

        for comment in wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "C4VMK"))):
            data.append(comment.text.split('\n')[1])

    return data[1:] #retirar a legenda