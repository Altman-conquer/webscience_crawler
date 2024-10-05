# selenium库
# 处理时间
import csv
import time

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from translate import translate_doubao

global_driver = None


# 发送请求
def askurl(url):
    global global_driver
    if global_driver is not None:
        driver = webdriver.Edge()
    else:
        driver = webdriver.Edge()
        global_driver = driver
    # 添加请求的头部
    # options = webdriver.EdgeOptions()								#开启启动参数
    # useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'													#写入自己的useragent
    # options.add_argument("user-agent:{}".format(useragent))
    # options.add_argument("--proxy-server = http://{}".format(ip))	#代理ip ip要写自己的

    # 开启模拟浏览器
    driver.get(url)

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

    check_status(driver)

    error_cnt = 0
    while True:
        try:
            if error_cnt >= 2:
                print('错误多次出现，强制返回')
                return None

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#SumAuthTa-DisplayName-author-en-0'))
            )
            break
        except Exception as e:
            print(e)
            input('出现错误, 请确认是否解决')
            error_cnt += 1

    addresses = []
    for i in range(0, 10):
        address_button = driver.find_elements(By.CSS_SELECTOR,
                                              f'#FRAOrgTa-addressesShowHideBtn-{i} > span.mat-button-wrapper')
        if len(address_button) > 0:
            address_button = address_button[0]

            try:
                address_button.click()
                address = driver.find_elements(By.CSS_SELECTOR, f'#FRAOrgTa-RepOrgEnhancedName-addresses-{i}-0')
            except Exception as e:
                address = driver.find_elements(By.CSS_SELECTOR,
                                               f'#address_{i + 1} > span.value.padding-right-5--reversible.section-label-data.colonMark')
        else:
            address = driver.find_elements(By.CSS_SELECTOR,
                                           f'#address_{i + 1} > span.value.padding-right-5--reversible.section-label-data.colonMark')

        if len(address) > 0:
            address = address[0].text.split(',')[0]
        else:
            break

        addresses.append(address)

    for index in range(0, 8):
        author_info = driver.find_elements(By.CSS_SELECTOR, f'#SumAuthTa-DisplayName-author-en-{index}')

        if len(author_info) == 0:
            break

        try:
            author_name = driver.find_element(By.CSS_SELECTOR,
                                              f'#SumAuthTa-FrAuthStandard-author-en-{index} > span').text
        except Exception as e:
            author_name = driver.find_element(By.CSS_SELECTOR, f'#SumAuthTa-DisplayName-author-en-{index} > span').text

        author_name = ' '.join(author_name.strip(' ').split(','))
        while author_name.find('  ') != -1:
            author_name = author_name.replace('  ', ' ')

        author_loc = driver.find_elements(By.CSS_SELECTOR, f'#SumAuthTa-FrAddrNbr-author-en-{index}-0')
        if len(author_loc) > 0:
            try:
                author_loc = int(author_loc[0].text.strip(' ').lstrip('[').rstrip(']'))
            except Exception as e:
                print("error at int(author_loc[0].text.strip(' ').lstrip('[').rstrip(']'))")
                print(e)
                author_loc = -1
        else:
            author_loc = -1

        authors.append(
            {
                'name': author_name,
                'url': driver.find_element(By.CSS_SELECTOR, f'#SumAuthTa-DisplayName-author-en-{index}').get_attribute(
                    'href'),
                'location': '' if author_loc == -1 else addresses[author_loc - 1]
            })

    # for author in authors:
    #     driver.get(author['url'])
    #
    #     # Wait for the element to be present with a timeout of 10 seconds
    #     try:
    #         # WebDriverWait(driver, 10).until(
    #         #     EC.presence_of_element_located((By.CSS_SELECTOR,
    #         #                                     'body > app-wos > main > div > div > div.holder.new-wos-style > div > div > div.held > app-input-route > app-author-page > div > div > div.author-details-section > app-author-record-header > div > div > div > mat-card-title > h1'))
    #         # )
    #         # author_name = driver.find_elements(By.CSS_SELECTOR,
    #         #                                    'body > app-wos > main > div > div > div.holder.new-wos-style > div > div > div.held > app-input-route > app-author-page > div > div > div.author-details-section > app-author-record-header > div > div > div > mat-card-title > h1')
    #         # if len(author_name) != 0 and author_name[0].text != '':
    #         #     author['name'] = author_name[0].text
    #         WebDriverWait(driver, 10).until(
    #             EC.presence_of_element_located((By.CSS_SELECTOR,
    #                                             'body > app-wos > main > div > div > div.holder.new-wos-style > div > div > div.held > app-input-route > app-author-page > div > div > div.author-details-section > app-author-record-header > div > div > div > mat-card-content > div.inline-container > span > span:nth-child(1)'))
    #         )
    #         author_loc = driver.find_elements(By.CSS_SELECTOR,
    #                                           'body > app-wos > main > div > div > div.holder.new-wos-style > div > div > div.held > app-input-route > app-author-page > div > div > div.author-details-section > app-author-record-header > div > div > div > mat-card-content > div.inline-container > span > span:nth-child(1)')
    #         if len(author_loc) != 0:
    #             author['location'] = author_loc[0].text
    #
    #
    #     except Exception as e:
    #         author['location'] = ''
    #         check_status(driver)

    return authors


def check_status(driver):
    """
    检查是否需要手动处理验证码
    :param driver:
    :return:
    """
    try:
        cookie_button = driver.find_elements(By.CSS_SELECTOR, '#onetrust-accept-btn-handler')
        if len(cookie_button) > 0:
            cookie_button[0].click()
    except Exception as e:
        pass

    while True:
        try:
            WebDriverWait(driver, 10).until_not(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '#mat-dialog-0 > app-captcha-details > div > div > div > p'))
            )
            break
        except Exception as e:
            print('请手动处理验证码')


def cataloge_page(url):
    driver = askurl(url)

    time.sleep(5)

    check_status(driver)

    # input('是否可以进行下一步')

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
                time.sleep(0.5)
            else:
                print(f'essay num: {len(essays)}')
                break

    for essay in essays:
        essay['authors'] = query_url(driver, essay['url'])
        print(essay['title'], essay['authors'])

    return essays


def main(urls: list[str]):
    essays = []
    for url in urls:
        essays.extend(cataloge_page(url))

    with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        translate_map = {'': ''}
        for essay in essays:
            row = [essay['title'], essay['url']]

            if essay.get('authors') is not None and len(essay.get('authors')) > 0:
                for author in essay['authors']:
                    if author['location'] != '' and translate_map.get(author['location']) is None:
                        location = translate_doubao(author['location'])
                        for missing_word in ['无法', '错误', '可能', '不够', '不全', '没有', '不够']:
                            if missing_word in location:
                                location = author['location']
                                break
                        translate_map[author['location']] = location

                row.extend(
                    [author['name'] + ', ' + translate_map.get(author['location']) for
                     author in essay['authors']]
                )
            writer.writerow(row)


def filter():
    with open('output_filter.txt', 'r', encoding='utf-8') as file:
        filter_journal = set(file.read().splitlines())

    with open('output.csv', 'r', encoding='utf-8') as file:
        data = file.read().splitlines()

    result = []
    for i in data:
        if i.split(',')[0] not in filter_journal:
            continue
        result.append(i + '\n')

    with open('output_filtered.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csvfile.writelines(result)


if __name__ == '__main__':
    main([
        'https://webofscience.clarivate.cn/wos/alldb/summary/2e8d2b82-2561-406c-a387-6575ad52fafa-010e3b7acb/date-descending/1'
    ])
    # filter()
