# 温馨提示:大佬往往都是要么不出现,要么扎堆出现
import csv
import re
from os import remove

import pandas as pd
import redis
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

redis_cli = redis.Redis(host='127.0.0.1',
                        port=6379, db=0)


# 这里是用本地的Microsoft Edge Driver和用户数据,不过selenium现在好像已经有包能实现不用本地的Microsoft Edge Driver了
def init_driver():
    driver = webdriver.Edge()
    return driver


def get_authors_information(csv_file_path):
    rows = []
    with open(csv_file_path, mode='r', newline='', encoding="utf-8") as csvfile:
        csvreader = csv.reader(csvfile)
        # 遍历每一行
        for row in csvreader:
            # 获取从第F列到第L列的数据，如果某列不存在，则返回"None"
            row_item = [cell for cell in row[5:] if cell]
            # print(row_item)
            rows.append(row_item)
    return rows


def google_scholar_helper(text):
    match = re.search(r'\d+', text)
    if match:
        return int(match.group())
    return 0


def using_google_scholar(driver, wait_time, rows, conf):
    driver.get("https://scholar.google.com")
    wait = WebDriverWait(driver, wait_time)
    rows_num = len(rows)

    remove_index = []
    for index_a, authors_information in enumerate(rows):
        print(f"当前进度: {index_a + 1}/{rows_num}")
        index_b = 0

        tag = False

        while index_b < len(authors_information):
            author_information = authors_information[index_b]

            if redis_cli.hget('google_scholar', author_information) is not None:
                if author_information in ['Abbod Maysam, Brunel University', 'Wang Jianqiang, Tsinghua University']:
                    print('test')
                tmp = redis_cli.hget('google_scholar', author_information).decode()
                if tmp == '':
                    index_b += 1
                    continue
                else:
                    rows[index_a][index_b] = tmp
                    index_b += 1
                    tag = True
                    continue

            author_information_split = author_information.split(",")
            if len(author_information_split) >= 3:
                index_b += 1
                continue
            author_name = author_information_split[0]
            input_element = wait.until(EC.presence_of_element_located((By.ID, "gs_hdr_tsi")))
            # 清空搜索栏
            input_element.clear()
            input_element.send_keys(f"{author_name}")
            # print(author_name)  # debug用
            input_element.send_keys(Keys.RETURN)
            try:
                cited_num = input(f'请输入{author_information}被引用次数:')
                if cited_num == '':
                    cited_num = 0
                else:
                    cited_num = int(cited_num)

                # if len(driver.find_elements(By.CSS_SELECTOR,
                #                             '#gs_res_ccl_mid > div:nth-child(1) > table > tbody > tr > td:nth-child(2) > div:nth-child(1)')) > 0:
                #     cited_num = input(f'请输入{author_information}被引用次数:')
                #     if cited_num == '':
                #         cited_num = 0
                #     else:
                #         cited_num = int(cited_num)
                # elif len(driver.find_elements())
                # else:
                #     key_element = driver.find_element(By.XPATH,
                #                                       "//div[(starts-with(text(), 'Počet citací tohoto článku: ') or starts-with(text(), '被引用次数：')) or (./h4 and contains(., '被引用次数：') and contains(., '电子邮件经过验证'))]")
                #     cited_num = google_scholar_helper(key_element.text)

                if cited_num >= conf:
                    tag = True
                    title = input("查询到关键字,请确认头衔(确认没有则按回车继续):")
                    if title != '':
                        new_author_information = author_information + ',' + title
                    else:
                        new_author_information = author_information

                    redis_cli.hset('google_scholar', author_information, new_author_information)

                    rows[index_a][index_b] = new_author_information
                else:
                    redis_cli.hset('google_scholar', author_information, '')

            except Exception as e:
                print(e)
                input('出现错误,请手动处理后按回车继续')
                pass

            index_b += 1

        if tag is False:
            remove_index.append(index_a)

    for index in remove_index[::-1]:
        rows[index] = ['none']
    return rows


def main():
    driver = init_driver()
    # 获取作者信息"姓名,学校"
    # 记得改路径
    csv_file_path = "output/result"
    rows = get_authors_information(csv_file_path + ".csv")
    # 使用。
    # conf就是阈值,这里设定总被引>7000才会关注
    # wait_time越短,越快
    rows = using_google_scholar(driver, wait_time=2, rows=rows, conf=7000)
    # 退出,并且保存
    # with open(csv_file_path + "_test" + ".csv", mode='w', newline='', encoding='utf-8') as csvfile:
    #     csvwriter = csv.writer(csvfile)
    #     # 写入每一行
    #     for row in rows:
    #         csvwriter.writerow(row)

    df = pd.read_csv(csv_file_path + ".csv", header=None)
    remove_index = []
    for index, row in enumerate(rows):
        if row[0] == 'none':
            remove_index.append(index)
        else:
            for i, cell in enumerate(row):
                df.iloc[index, i + 5] = cell
    df.drop(remove_index, inplace=True)
    df.to_csv(csv_file_path + "_result.csv", header=None, index=None)


    driver.quit()



if __name__ == '__main__':
    main()
