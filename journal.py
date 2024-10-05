import csv
import re
import time

from openai import OpenAI

from settings import KIMI_API_KEY


def main():
    with open('journal.txt', 'r', encoding='utf-8') as file:
        data = file.read().splitlines()

    journal_set = set(data)

    with open('journal_map.csv', 'r', encoding='utf-8') as file:
        tmp_str = file.read()
        journal_map = {}
        for line in tmp_str.splitlines():
            tmp_arr = line.split(',')
            journal, zone = ','.join(tmp_arr[:-1]), tmp_arr[-1]
            journal_map[journal] = zone
            journal_set.discard(journal)

    client = OpenAI(
        api_key=KIMI_API_KEY,
        base_url="https://api.moonshot.cn/v1",
    )

    for journal in journal_set:
        if journal == '':
            journal_map[journal] = ''
            continue

        if journal_map.get(journal) is not None:
            print(f'{journal} is already mapped to {journal_map.get(journal)}')
            continue

        completion = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system",
                 "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。回答要简洁，不要有多余文字"},
                {"role": "user", "content": f"{journal}是中科院几区的文章，只需要回答是几区，不需要其他文字"}
            ],
            temperature=0.3,
        )

        res = completion.choices[0].message.content.strip('。')
        if not res.startswith('中科院'):
            res = '中科院' + res

        journal_map[journal] = res

        print(journal, res)

        time.sleep(30)

    with open('journal_map.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows([[journal, journal_map[journal]] for journal in journal_map])

    with open('journal.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows([[journal, journal_map[journal]] for journal in data])


def temp():
    with open('journal._map.txt', 'r', encoding='utf-8') as file:
        data = file.read().splitlines()

    journal_map = {}
    for line in data:
        tmp = line.split(' ')
        journal = ' '.join(tmp[:-1])
        zone = tmp[-1]
        # replace '将...为' to ''
        zone = re.sub(r'将.*为', '', zone)

        zone = zone.replace('"', '')

        # replace 1,2,3,4 to 一，二，三，四
        zone = zone.replace('1', '一').replace('2', '二').replace('3', '三').replace('4', '四')

        if zone == '':
            zone = '未分区'

        journal_map[journal] = zone

    # with open('journal_map.csv', 'w', newline='', encoding='utf-8') as csvfile:
    #     writer = csv.writer(csvfile)
    #     writer.writerows([[journal, journal_map[journal]] for journal in journal_map])


def format_csv():
    with open('journal.csv', 'r', encoding='utf-8') as file:
        data = file.read().splitlines()

    result = []
    for line in data:
        tmp = line.split(',')
        journal = ' '.join(tmp[:-1])
        zone = tmp[-1]
        # replace '将...为' to ''
        zone = re.sub(r'将.*为', '', zone)

        # replace 1,2,3,4 to 一，二，三，四
        zone = zone.replace('1', '一').replace('2', '二').replace('3', '三').replace('4', '四')
        result.append([journal, zone])

    with open('journal_formatted.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(result)


if __name__ == '__main__':
    # temp()
    main()
    format_csv()
