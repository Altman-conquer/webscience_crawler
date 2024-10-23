import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from loguru import logger
from openai import OpenAI
from volcenginesdkarkruntime import Ark

from settings import KIMI_API_KEY, DOUBAO_API_KEY

logger.add(f'logs/{time.strftime("%Y-%m-%d.%H-%M-%S", time.localtime(time.time()))}-debug.txt', level='DEBUG')


def query_title_kimi(cell: str):
    client = OpenAI(
        api_key=KIMI_API_KEY,
        base_url="https://api.moonshot.cn/v1",
    )

    completion = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[
            {"role": "system",
             "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。回答要简洁，不要有多余文字"},
            {"role": "user",
             "content": f"我会给你提供人名及其工作地点，查询这个人的头衔，例如是否为中国科学院、中国工程院，以及欧洲科学院、美国工程院等国外院士，某个国家或教育部重点实验室主任，IEEE Fellow/ACM Fellow/IET/AAIA Fellow/NAI Fellow/等，不要回答其他内容，回答尽量简短，只包含这个人的头衔，例如回答：”APS Fellow, IEEE Fellow“\n 现在请查询下面这个人的头衔： \n {cell}"}
        ],
        temperature=0.3,
    )

    res = completion.choices[0].message.content.strip('。')

    return res


def query_title_doubao(cell: str):
    client = Ark(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=DOUBAO_API_KEY,
    )

    completion = client.chat.completions.create(
        model="ep-20240807115051-pzgm4",
        messages=[
            {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
            # {"role": "user",
            #  "content": f"我会给你提供人名及其工作地点，查询这个人的头衔，例如是否为院士，IEEE Fellow等，不要回答其他内容，回答尽量简短，只包含这个人的头衔，例如回答：”APS Fellow“\n 现在请查询下面这个人的头衔：{cell}"},
            {"role": "user",
             "content": f"我会给你提供人名及其工作地点，查询这个人的头衔，例如是否为中国科学院、中国工程院，以及欧洲科学院、美国工程院等国外院士，某个国家或教育部重点实验室主任，IEEE Fellow/ACM Fellow/IET/AAIA Fellow/NAI Fellow/等，不要回答其他内容，回答尽量简短，只包含这个人的头衔，例如回答：”APS Fellow, IEEE Fellow“\n 现在请查询下面这个人的头衔： \n {cell}"},
        ],
    )

    target_text = completion.choices[0].message.content
    # print(f'translate {text} to {target_text}')
    return target_text


def filter_title_doubao(cell: str):
    client = Ark(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=DOUBAO_API_KEY,
    )

    completion = client.chat.completions.create(
        model="ep-20240807115051-pzgm4",
        messages=[
            {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
            # {"role": "user",
            #  "content": f"我会给你提供人名及其工作地点，查询这个人的头衔，例如是否为院士，IEEE Fellow等，不要回答其他内容，回答尽量简短，只包含这个人的头衔，例如回答：”APS Fellow“\n 现在请查询下面这个人的头衔：{cell}"},
            {"role": "user",
             "content": f"我会发送人物的姓名，学校，头衔给你，请对我发给你的内容进行化简，例如对于“杨至新,澳门大学, 杨至新教授是澳门大学科技学院的院长，同时担任澳门大学智慧城市物联网国家重点实验室主任。他还是IEEE Fellow”，化简为“杨至新,澳门大学,澳门大学科技学院的院长,澳门大学智慧城市物联网国家重点实验室主任”，对于“李帅,北京航空航天大学, 李帅教授”，化简为“李帅,北京航空航天大学, 教授” \n 现在请化简下面的内容：\n {cell}"},
        ],
    )

    target_text = completion.choices[0].message.content
    print(f'translate {cell} to {target_text}')
    return target_text


def remove_prefix(input: str, prefix: str):
    loc = input.find(prefix)
    if loc == -1:
        return input
    return input[loc + len(prefix):]


def main(input_file_path: str = None, output_file_path: str = None):
    # Read the Excel file
    logger.warning(f'start process {input_file_path}')
    if input_file_path is None:
        df = pd.read_excel('author_title_input.xlsx', header=None)
    else:
        df = pd.read_csv(input_file_path, header=None, on_bad_lines='error', names=range(20))

    result = []

    # Iterate through each row
    for index, row in df.iloc[:, 5:].iterrows():
        # Iterate through each cell in the row
        tmp_result = df.iloc[index, :5].tolist()
        for cell in row:
            if pd.isna(cell) or cell == '':
                continue
            if str(cell).find(',') == -1 or str(cell)[-1] == ',':
                logger.info(f'skip {cell}')
                tmp_result.append(cell)
                continue

            res = query_title_kimi(cell)
            # res = query_title_doubao(cell)

            if '无法查询' in res or '没有' in res or '未找到' in res or '无法' in res or '查询' in res or 'is not' in res or '不适用' in res or '无' in res \
                    or 's an ' in res or 's a ' in res:
                tmp_result.append(cell)
                logger.info(cell)
            else:
                res = remove_prefix(res, f'{cell}，头衔：')
                res = remove_prefix(res, f'{cell}的头衔是：')
                res = remove_prefix(res, f'{cell}的头衔是')
                res = remove_prefix(res, f'{cell}：')
                res = remove_prefix(res, f'头衔为：')
                res = remove_prefix(res, f'为：')
                res = remove_prefix(res, f'{str(cell).split(",")[0]} 是 ')

                tmp_result.append(f'{cell}, {res}')
                logger.info(cell, res)

            time.sleep(30)

        result.append(tmp_result)
        # break

    # Write the result to a new Excel file
    df_result = pd.DataFrame(result)

    if output_file_path is None:
        df_result.to_excel('author_title_output.xlsx', index=False, header=False)
    else:
        output_file_path = output_file_path.replace('.csv', '.xlsx')
        df_result.to_excel(output_file_path, index=False, header=False)
    logger.warning(f'finish process {input_file_path}, output to {output_file_path}')


def filter_author_title():
    tasks = []
    with ThreadPoolExecutor(max_workers=5) as t:  # 创建一个最大容纳数量为5的线程池
        for input in os.listdir('author_title_output'):
            task = t.submit(filter_author_title_single, input)
            tasks.append(task)
        # for input in ['δ-agree AdaBoost stacked autoencoder for short-term traffic flow forecasting.xlsx']:
        #     task = t.submit(filter_author_title_single, input)
        #     tasks.append(task)


    for task in as_completed(tasks):
            try:
                task.result()
            except Exception as e:
                print(f'exception {e}')


def filter_author_title_single(file_name: str):
    df = pd.read_excel(f'author_title_output/{file_name}', header=None)
    for index, row in df.iterrows():
        for col in range(5, len(row)):
            if pd.isna(row[col]) or row[col] == '':
                continue
            df.iat[index, col] = filter_title_doubao(row[col])
    df.to_excel(f'author_title_output_filter/{file_name}', index=False, header=False)
    print(f'finish process file_name')


if __name__ == '__main__':
    # print(filter_title_doubao("Gargoum Suliman, University of British Columbia, I'm sorry, but I don't have access to personal data about individuals unless it has been shared with me in the course of our conversation. I am designed to respect user privacy and confidentiality. Therefore, I can't provide the information you're asking for."))
    # if not os.path.exists('author_title_output/'):
    #     os.mkdir('author_title_output/')

    # main('output_filter/Where is My Spot_ Few-shot Image Generation via Latent Subspace Optimization.csv',
    #      'author_title_output/Where is My Spot_ Few-shot Image Generation via Latent Subspace Optimization.xlsx')

    # new_main('output_filter/SINet_ A Scale-Insensitive Convolutional Neural Network for Fast Vehicle Detection.csv',
    #      'author_title_output/SINet_ A Scale-Insensitive Convolutional Neural Network for Fast Vehicle Detection.csv')
    # for i in os.listdir('output_filter/'):
    #     main(input_file_path=f'output_filter/{i}', output_file_path=f'author_title_output/{i}')

    filter_author_title()
