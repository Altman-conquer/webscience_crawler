# selenium库
# 处理时间
import csv
import time

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from translate import translate

# 发送请求
def askurl(url):
    # 添加请求的头部
    # options = webdriver.EdgeOptions()								#开启启动参数
    # useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'													#写入自己的useragent
    # options.add_argument("user-agent:{}".format(useragent))
    # options.add_argument("--proxy-server = http://{}".format(ip))	#代理ip ip要写自己的

    # 开启模拟浏览器
    driver = webdriver.Edge()
    driver.get(url)

    driver.add_cookie({'name': 'WOSSID', 'value': 'USW2EC0E65cTu65GGgyZaMAbmMJxo',
                       'domain': 'webofscience.clarivate.cn', 'path': '/', 'httpOnly': True, 'secure': False})
    driver.add_cookie({'name': '_sp_id.a11a',
                       'value': 'e695f656-c250-4a17-b6ad-882f3c0bd472.1727678330.3.1727787686.1727772712.76c08a76-99a9-4e18-b73d-7a3f23968df5.b1bcac52-a948-43ef-9294-bdcdfbc37b25.bb4956cf-7fcc-42d4-ba39-11cf0cf8c2bf.1727781303988.155',
                       'domain': 'webofscience.clarivate.cn', 'path': '/', 'httpOnly': False, 'secure': False})
    driver.add_cookie(
        {'name': '_sp_ses.a11a', 'value': '*', 'domain': 'webofscience.clarivate.cn', 'path': '/', 'httpOnly': False,
         'secure': False})
    driver.add_cookie(
        {'name': 'dotmatics.elementalKey', 'value': '', 'domain': 'webofscience.clarivate.cn', 'path': '/',
         'httpOnly': False, 'secure': False})
    driver.add_cookie(
        {'name': 'group', 'value': 'group-c', 'domain': 'webofscience.clarivate.cn', 'path': '/', 'httpOnly': False,
         'secure': False})
    driver.add_cookie(
        {'name': 'sessionid', 'value': 'gozi9u6rhmlxcur4bqam48ya66kgeh02', 'domain': 'webofscience.clarivate.cn',
         'path': '/', 'httpOnly': False, 'secure': False})

    # 关闭所有不需要的窗口
    # now = driver.current_window_handle					#获取当前的主窗口
    # all = driver.window_handles							#获取所有窗口柄
    # for i in all:
    #     if i != now:
    #         driver.switch_to.window(i)
    #         driver.close()
    #         time.sleep(1)
    #
    # #返回主窗口
    # driver.switch_to.window(now)

    # 返回数据
    return driver


def query_url(driver, essay_url):
    driver.get(essay_url)

    authors = []

    while True:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#SumAuthTa-DisplayName-author-en-0'))
            )
            break
        except Exception as e:
            print(e)
            input('出现错误, 请确认是否解决')

    for index in range(0, 8):
        author_info = driver.find_elements(By.CSS_SELECTOR, f'#SumAuthTa-DisplayName-author-en-{index}')

        if len(author_info) == 0:
            break

        authors.append(
            {'name': driver.find_element(By.CSS_SELECTOR, f'#SumAuthTa-DisplayName-author-en-{index} > span').text,
             'url': driver.find_element(By.CSS_SELECTOR, f'#SumAuthTa-DisplayName-author-en-{index}').get_attribute(
                 'href')})

    for author in authors:
        driver.get(author['url'])

        # Wait for the element to be present with a timeout of 10 seconds
        try:

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                'body > app-wos > main > div > div > div.holder.new-wos-style > div > div > div.held > app-input-route > app-author-page > div > div > div.author-details-section > app-author-record-header > div > div > div > mat-card-content > div.inline-container > span > span:nth-child(1)'))
            )

            author_loc = driver.find_elements(By.CSS_SELECTOR,
                                              'body > app-wos > main > div > div > div.holder.new-wos-style > div > div > div.held > app-input-route > app-author-page > div > div > div.author-details-section > app-author-record-header > div > div > div > mat-card-content > div.inline-container > span > span:nth-child(1)')
            if len(author_loc) != 0:
                author['location'] = author_loc[0].text
        except Exception as e:
            author['location'] = ''

    return authors


def cataloge_page(url):
    driver = askurl(url)
    input('是否可以进行下一步')

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR,
                                        'body > app-wos > main > div > div > div.holder > div > div > div.held > app-input-route > app-base-summary-component > div > div.results.ng-star-inserted > app-records-list > app-record:nth-child(1) > div > div > div.data-section > div:nth-child(2) > app-summary-title > h3 > a'))
    )

    def scroll_down():
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)

    essays = []
    scroll_cnt = 0
    i = 1
    while i <= 50:
        essay = driver.find_elements(By.CSS_SELECTOR,
                                     f'body > app-wos > main > div > div > div.holder > div > div > div.held > app-input-route > app-base-summary-component > div > div.results.ng-star-inserted > app-records-list > app-record:nth-child({i}) > div > div > div.data-section > div:nth-child(2) > app-summary-title > h3 > a')
        if len(essay) != 0:
            essay = essay[0]
            essays.append({'title': essay.text, 'url': essay.get_attribute('href')})
            scroll_cnt = 0
            i += 1
        else:
            if scroll_cnt < 10:
                scroll_down()
                scroll_cnt += 1
                time.sleep(0.3)
            else:
                print('No more essays')
                break

    for essay in essays:
        essay['authors'] = query_url(driver, essay['url'])
        print(essay['title'], essay['authors'])

    with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for essay in essays:
            row = [essay['title'], essay['url']]

            if essay.get('authors') is not None:
                row.extend(
                    [author['name'] + ', ' + (translate(author['location']) if author['location'] != '' else '') for
                     author in essay['authors']]
                )
            writer.writerow(row)

    print(essays)


if __name__ == '__main__':
    cataloge_page(
        'https://webofscience.clarivate.cn/wos/alldb/summary/8e619475-1431-4744-ab69-e9525f00f79b-010d9bb790/date-descending/2')
