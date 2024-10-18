# selenium库
# 处理时间
import csv
import os.path
import re
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from journal import get_journal_zone_kimi
from translate import translate_doubao

global_driver = None


# 发送请求
def askurl(url):
    global global_driver
    if global_driver is not None:
        driver = global_driver
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

    driver.maximize_window()

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


def get_journal_zone(driver, essay_name: str = ''):
    try:
        def scroll_to_top():
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.HOME)
            time.sleep(0.5)

        time.sleep(0.5)
        scroll_to_top()
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            '#snMainArticle > div:nth-child(6) > span > app-jcr-sidenav > mat-sidenav-container > mat-sidenav-content'))
        )
        driver.find_element(By.CSS_SELECTOR,
                            '#snMainArticle > div:nth-child(6) > span > app-jcr-sidenav > mat-sidenav-container > mat-sidenav-content').click()
        time.sleep(0.5)
        driver.find_element(By.CSS_SELECTOR, 'div.mat-menu-content > a:first-of-type').click()
        time.sleep(0.5)
        zone: str = driver.find_element(By.CSS_SELECTOR, '#Sidenav-0-JCR-quartile_0').text
        zone = zone.removeprefix('Q')
        zone = zone.replace('1', '一区').replace('2', '二区').replace('3', '三区').replace('4', '四区')
    except Exception as e:
        return get_journal_zone_kimi(essay_name)
    return 'JCR ' + zone


def query_url(driver, essay_url):
    driver.get(essay_url)

    authors = []

    check_status(driver)

    error_cnt = 0
    while True:
        try:
            if error_cnt >= 2:
                print('错误多次出现，强制返回')
                return None, None, None, None

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#SumAuthTa-DisplayName-author-en-0'))
            )
            break
        except Exception as e:
            print(e)
            return None, None, None, None
            input('出现错误, 请确认是否解决')
            error_cnt += 1

    more_address_button = driver.find_elements(By.CSS_SELECTOR, '#FRACTa-authorAddressView')
    if len(more_address_button) > 0:
        more_address_button = more_address_button[0]
        more_address_button.click()

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

        try:
            location = '' if author_loc == -1 else addresses[author_loc - 1]
        except Exception as e:
            location = ''

        authors.append(
            {
                'name': author_name,
                'url': driver.find_element(By.CSS_SELECTOR, f'#SumAuthTa-DisplayName-author-en-{index}').get_attribute(
                    'href'),
                'location': location
            })

    journal = driver.find_elements(By.CSS_SELECTOR,
                                   '#snMainArticle > div.cdx-two-column-grid-container.ng-star-inserted > span > app-jcr-sidenav > mat-sidenav-container > mat-sidenav-content > span > a > span')
    if len(journal) == 0:
        journal = driver.find_elements(By.CSS_SELECTOR,
                                       '#snMainArticle > div.cdx-two-column-grid-container.ng-star-inserted > span > app-jcr-sidenav > mat-sidenav-container > mat-sidenav-content > span > span')

    if len(journal) > 0:
        journal = journal[0].text

    year = driver.find_elements(By.CSS_SELECTOR, '#FullRTa-indexedDate')
    if len(year) > 0:
        year = year[0].text.split('-')[0]

    zone = get_journal_zone(driver, journal)

    return authors, journal, year, zone


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

    try:
        tutorial_button = driver.find_elements(By.CSS_SELECTOR, '_pendo-close-guide')
        if len(tutorial_button) > 0:
            tutorial_button[0].click()
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
        check_status(driver)

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
        essay['authors'], essay['journal'], essay['year'], essay['zone'] = query_url(driver, essay['url'])
        print(essay['title'], essay['journal'], essay['zone'], essay['year'], essay['authors'])

    return essays


def get_cited_essay_name(url: str):
    driver = askurl(url)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#GenericFD-article-metadata-parent > span > span'))
        )
    except Exception as e:
        return url
    essay_name = driver.find_element(By.CSS_SELECTOR, '#GenericFD-article-metadata-parent > span > span').text
    return sanitize_filename(essay_name)


def sanitize_filename(filename):
    # 定义不允许的字符
    invalid_chars = r'[<>:"/\\|?*]'
    # 使用下划线替换不允许的字符
    sanitized_filename = re.sub(invalid_chars, '', filename)
    return sanitized_filename


def main(urls: list[str]):
    print(f'start process {urls}')

    try:
        essays = []
        for url in urls:
            essays.extend(cataloge_page(url))

        essay_name = get_cited_essay_name(urls[0])

        # make sure output directory exist
        if not os.path.exists('output/'):
            os.mkdir('output')

        with open(f'output/{essay_name}.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            translate_map = {'': ''}
            for essay in essays:
                row = [essay['title'], essay['url']]

                if essay.get('journal') is not None:
                    row.extend([essay['journal']])
                if essay.get('year') is not None:
                    row.extend([essay['year']])
                if essay.get('zone') is not None:
                    row.extend([essay['zone']])

                if essay.get('authors') is not None and len(essay.get('authors')) > 0:
                    # for author in essay['authors']:
                    #     if author['location'] != '' and translate_map.get(author['location']) is None:
                    #         # location = translate_kimi(f'{author["name"]}, {author["location"]}')
                    #         location = translate_doubao(f'{author["name"]}, {author["location"]}')
                    #         for missing_word in ['无法', '错误', '可能', '不够', '不全', '没有', '不够']:
                    #             if missing_word in location:
                    #                 location = f'{author["name"]}, {author["location"]}'
                    #                 break
                    #         translate_map[author['location']] = location

                    # row.extend(
                    #     [author['name'] + ', ' + translate_map.get(author['location']) for
                    #      author in essay['authors']]
                    # )

                    # row.extend(
                    #     [translate_kimi(f'{author["name"]}, {author["location"]}') for
                    #      author in essay['authors']]
                    # )

                    # row.extend(
                    #     [translate_doubao(f'{author["name"]}, {author["location"]}') for
                    #      author in essay['authors']]
                    # )
                    row.extend(
                        [f'{author["name"]}, {author["location"]}' for
                         author in essay['authors']]
                    )
                writer.writerow(row)
    except Exception as e:
        print(f'error when processing {urls}, error: {e}')


def filter(filter_journal: list[str] = None, data: list[str] = None, output_file_path: str = None):
    if filter_journal is None:
        with open('output_filter.txt', 'r', encoding='utf-8') as file:
            text = file.read()
            text = text.replace('\n\n', '\ntest\n')
            filter_journal = text.splitlines()

    if data is None:
        with open('output.csv', 'r', encoding='utf-8') as file:
            data = file.read().splitlines()

    result = []

    j = 0
    for i in range(0, len(data)):
        if filter_journal[j] == 'test':
            result.append('\n')
            j += 1
            continue
        if data[i].split(',')[0] not in set(filter_journal):
            continue
        result.append(data[i] + '\n')
        j += 1

        if j > len(filter_journal) - 1:
            break
    # for i in data:
    #     if i == ' ':
    #         result.append('\n')
    #     if i.split(',')[0] not in filter_journal:
    #         continue
    #     result.append(i + '\n')

    if output_file_path is None:
        with open('output_filtered.csv', 'w', newline='', encoding='utf-8') as csvfile:
            csvfile.writelines(result)
    else:
        with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csvfile.writelines(result)


def auto_filter():
    input_files = [f for f in os.listdir('input/')]
    output_files = [f for f in os.listdir('output/')]

    def get_input_essay_name(input_file_name: str):
        input_file_name = input_file_name.replace('.xlsx', '')
        input_file_name = input_file_name.replace('论文同行评价-2018-TITS-（总引用数）- ', '')
        input_file_name = input_file_name.replace('论文同行评价-2018-TITS-（总引用数） - ', '')
        input_file_name = sanitize_filename(input_file_name)
        return input_file_name

    for input_file in input_files:
        essay_name = get_input_essay_name(input_file)
        output_file_name = ''
        for j in output_files:
            if essay_name.lower() in j.replace('_', '').lower():
                output_file_name = j
                break
        if output_file_name == '':
            while True:
                output_file_name = input(f'无法找到{essay_name}对应的输入文件，请手动输入')
                if os.path.exists(f'output/{output_file_name}'):
                    break

        df = pd.read_excel(f'input/{input_file}')
        filter_journals = df.iloc[1:, 1].to_list()

        with open(f'output/{output_file_name}', 'r', encoding='utf-8') as file:
            data = file.read().splitlines()

        if not os.path.exists('output_filter/'):
            os.mkdir('output_filter/')

        filter(filter_journals, data, f'output_filter/{output_file_name}')


def test():
    df = pd.read_excel(
        'input/论文同行评价-2018-TITS-（总引用数）- SINet A Scale-insensitive Convolutional Neural Network for Fast Vehicle Detection.xlsx')
    print(df.head())


def get_file_name(url: list[str]):
    url = url[0]

    driver = askurl(url)
    time.sleep(5)

    check_status(driver)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#GenericFD-article-metadata-parent > span > span'))
        )
    except Exception as e:
        pass
    essay_name = driver.find_element(By.CSS_SELECTOR, '#GenericFD-article-metadata-parent > span > span').text
    essay_name = sanitize_filename(essay_name)

    driver.find_element(By.CSS_SELECTOR, '#GenericFD-article-metadata-parent').click()
    time.sleep(5)

    journal = driver.find_elements(By.CSS_SELECTOR,
                                   '#snMainArticle > div.cdx-two-column-grid-container.ng-star-inserted > span > app-jcr-sidenav > mat-sidenav-container > mat-sidenav-content > span > a > span')
    if len(journal) == 0:
        journal = driver.find_elements(By.CSS_SELECTOR,
                                       '#snMainArticle > div.cdx-two-column-grid-container.ng-star-inserted > span > app-jcr-sidenav > mat-sidenav-container > mat-sidenav-content > span > span')

    if len(journal) > 0:
        journal = journal[0].text
    else:
        journal = '无刊物名称'

    year = driver.find_elements(By.CSS_SELECTOR, '#FullRTa-indexedDate')
    if len(year) > 0:
        year = year[0].text.split('-')[0]

    files = os.listdir('input')
    df = []

    for file in files:
        if essay_name in file:
            df = pd.read_excel(f'input/{file}')
            break
            # with open(f'input/{file}', 'r', encoding='utf-8') as file:
            #     data = file.read().splitlines()


    res = f'{year}-{journal}刊物-{len(df) - 1}次引用-{essay_name}'
    print(res)

    return res


if __name__ == '__main__':
    # test()
    get_file_name([
        'https://webofscience.clarivate.cn/wos/alldb/summary/bcf63107-06d4-4c5d-87b9-73962fb158e4-0110e77550/date-descending/1',
        'https://webofscience.clarivate.cn/wos/alldb/summary/bcf63107-06d4-4c5d-87b9-73962fb158e4-0110e77550/date-descending/2',
        'https://webofscience.clarivate.cn/wos/alldb/summary/bcf63107-06d4-4c5d-87b9-73962fb158e4-0110e77550/date-descending/3',
    ])
    get_file_name([
        'https://webofscience.clarivate.cn/wos/alldb/summary/5cbdfa7b-735e-4f41-9ee2-49c8d8afc41f-0110e7c723/date-descending/1',
        'https://webofscience.clarivate.cn/wos/alldb/summary/5cbdfa7b-735e-4f41-9ee2-49c8d8afc41f-0110e7c723/date-descending/2'])
    get_file_name([
        'https://webofscience.clarivate.cn/wos/alldb/summary/6807229e-9aca-4f2b-9bbd-95e66bcefe59-0110e7cf50/date-descending/1'])
    get_file_name([
        'https://webofscience.clarivate.cn/wos/alldb/summary/c2d62e63-b8c4-4cd0-869e-2087300e5c4b-0110e7d885/date-descending/1'])
    get_file_name([
        'https://webofscience.clarivate.cn/wos/alldb/summary/4c7678b8-4763-43c4-aa1a-3989b43bbd28-0110e7df99/date-descending/1'])
    get_file_name([
        'https://webofscience.clarivate.cn/wos/alldb/summary/1623c323-e38c-482c-99fe-686f69b8f345-0110e7e488/date-descending/1'])
    get_file_name([
        'https://webofscience.clarivate.cn/wos/alldb/summary/f3033b9a-aee7-45a1-9797-d83fa5dcb3c9-0110e80818/date-descending/1'])
    get_file_name([
        'https://webofscience.clarivate.cn/wos/alldb/summary/6c24a003-6005-4e66-afcd-6540c56b1b8e-0110fcb796/date-descending/1'])
    get_file_name([
        'https://webofscience.clarivate.cn/wos/alldb/summary/a43d9e6d-f8f9-4855-80e5-396203455349-0110e81494/date-descending/1'])
    get_file_name([
        'https://webofscience.clarivate.cn/wos/alldb/summary/c13c63aa-af10-4d73-96cc-41a42e464c35-0110e81c12/date-descending/1'])
    get_file_name([
        'https://webofscience.clarivate.cn/wos/alldb/summary/a94e0c73-b588-4923-8e63-6f84386e15af-0110e81f3b/date-descending/1'])
    get_file_name([
        'https://webofscience.clarivate.cn/wos/alldb/summary/4917ca88-b582-495c-8e00-912a1780c0a5-0110e823d0/date-descending/1'])
    get_file_name([
        'https://webofscience.clarivate.cn/wos/alldb/summary/e054d476-625f-4635-ac20-ca55397df531-0110e82a1f/date-descending/1'])

    get_file_name([
        'https://webofscience.clarivate.cn/wos/alldb/summary/6c24a003-6005-4e66-afcd-6540c56b1b8e-0110fcb796/date-descending/1'])

    # filter()
    # auto_filter()
