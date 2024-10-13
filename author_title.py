import csv
import os
from os import remove

import pandas as pd
from openai import OpenAI
from volcenginesdkarkruntime import Ark

from settings import KIMI_API_KEY, DOUBAO_API_KEY


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
             "content": f"我会给你提供人名及其工作地点，查询这个人的头衔，例如是否为院士，IEEE Fellow等，不要回答其他内容，回答尽量简短，只包含这个人的头衔，例如回答：”APS Fellow“\n 现在请查询下面这个人的头衔：{cell}"}
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


def remove_prefix(input: str, prefix: str):
    loc = input.find(prefix)
    if loc == -1:
        return input
    return input[loc + len(prefix):]


def main(input_file_path: str = None, output_file_path: str = None):
    # Read the Excel file
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
                print(f'skip {cell}')
                tmp_result.append(cell)
                continue

            # res = query_title_kimi(cell)
            res = query_title_doubao(cell)

            if '无法查询' in res or '没有' in res or '未找到' in res or '无法' in res or '查询' in res or 'is not' in res or '不适用' in res or '无' in res \
                    or 's an ' in res or 's a ' in res:
                tmp_result.append(cell)
                print(cell)
            else:
                res = remove_prefix(res, f'{cell}，头衔：')
                res = remove_prefix(res, f'{cell}的头衔是：')
                res = remove_prefix(res, f'{cell}的头衔是')
                res = remove_prefix(res, f'{cell}：')
                res = remove_prefix(res, f'头衔为：')
                res = remove_prefix(res, f'为：')
                res = remove_prefix(res, f'{str(cell).split(",")[0]} 是 ')

                tmp_result.append(f'{cell}, {res}')
                print(cell, res)

            # time.sleep(30)

        result.append(tmp_result)
        # break

    # Write the result to a new Excel file
    df_result = pd.DataFrame(result)

    if output_file_path is None:
        df_result.to_excel('author_title_output.xlsx', index=False, header=False)
    else:
        output_file_path = output_file_path.replace('.csv', '.xlsx')
        df_result.to_excel(output_file_path, index=False, header=False)

if __name__ == '__main__':
    if not os.path.exists('author_title_output/'):
        os.mkdir('author_title_output/')

    # main('output_filter/Where is My Spot_ Few-shot Image Generation via Latent Subspace Optimization.csv',
    #      'author_title_output/Where is My Spot_ Few-shot Image Generation via Latent Subspace Optimization.xlsx')

    # new_main('output_filter/SINet_ A Scale-Insensitive Convolutional Neural Network for Fast Vehicle Detection.csv',
    #      'author_title_output/SINet_ A Scale-Insensitive Convolutional Neural Network for Fast Vehicle Detection.csv')
    for i in os.listdir('output_filter/'):
        main(input_file_path=f'output_filter/{i}', output_file_path=f'author_title_output/{i}')
