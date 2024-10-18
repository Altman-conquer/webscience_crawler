import time

import pandas as pd
from numba.cuda.simulator.cudadrv.driver import driver
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

global_driver = None


# 发送请求
def askurl(url):
    global global_driver
    if global_driver is not None:
        driver = global_driver
    else:
        driver = webdriver.Edge()
        global_driver = driver
    driver.get(url)
    driver.maximize_window()
    time.sleep(3)
    return driver

def search(essay_name):
    driver = askurl('https://webofscience.clarivate.cn/wos/alldb/basic-search')
    driver.find_element(By.CSS_SELECTOR, '#search-option').send_keys(essay_name)
    driver.find_element(By.CSS_SELECTOR, '#snSearchType > div.button-row > button.mat-focus-indicator.search.mat-flat-button.mat-button-base.mat-primary').click()

def filter_database(driver: webdriver.Edge):
    driver.find_element(By.CSS_SELECTOR, '#filter-section-SILOID > button').click()


def main():
    # search('Multi-view Face Synthesis via Progressive Face Flow')
    driver = askurl('https://webofscience.clarivate.cn/wos/alldb/summary/c9e7b8dc-892b-45ca-ab08-ff06f4519bb5-0111e5030c/date-descending/1')
    filter_database(driver)

if __name__ == '__main__':
    main()