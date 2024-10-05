import json

from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.tmt.v20180321 import tmt_client, models
from volcenginesdkarkruntime import Ark

from settings import TENCENT_API_KEY, TENCENT_API_SECRET, AZURE_TRANSLATE_KEY, DOUBAO_API_KEY


def translate(text):
    if text is None or text == '':
        return ''

    try:
        # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
        # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议采用更安全的方式来使用密钥，请参见：https://cloud.tencent.com/document/product/1278/85305
        # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
        cred = credential.Credential(TENCENT_API_KEY, TENCENT_API_SECRET)
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tmt.tencentcloudapi.com"

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        client = tmt_client.TmtClient(cred, "ap-guangzhou", clientProfile)

        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.TextTranslateRequest()
        params = {
            "SourceText": text,
            "Source": "en",
            "Target": "zh",
            "ProjectId": 0
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个TextTranslateResponse的实例，与请求对象对应
        resp = client.TextTranslate(req)
        # 输出json格式的字符串回包
        # print(resp.to_json_string())
        target_text = json.loads(resp.to_json_string()).get('TargetText')
        print(f'translate {text} to {target_text}')
        return target_text
    except TencentCloudSDKException as err:
        print(err)
        return ''


def translate_azure(text):
    import requests, uuid

    # Add your key and endpoint
    key = AZURE_TRANSLATE_KEY
    endpoint = "https://api.cognitive.microsofttranslator.com"

    # location, also known as region.
    # required if you're using a multi-service or regional (not global) resource. It can be found in the Azure portal on the Keys and Endpoint page.
    location = "global"

    path = '/translate'
    constructed_url = endpoint + path

    params = {
        'api-version': '3.0',
        'from': 'en',
        'to': ['zh']
    }

    headers = {
        'Ocp-Apim-Subscription-Key': key,
        # location required if you're using a multi-service or regional (not global) resource.
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # You can pass more than one object in body.
    body = [{
        'text': text
    }]

    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()

    return response[0].get('translations')[0].get('text')


def translate_doubao(text):
    client = Ark(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=DOUBAO_API_KEY,
    )

    completion = client.chat.completions.create(
        model="ep-20240807115051-pzgm4",
        messages=[
            {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
            {"role": "user",
             "content": f"将后面的内容翻译成中文，不要回答其他多余文字和符号，只需要返回一个结果\n\n{text}"},
        ],
    )

    target_text = completion.choices[0].message.content
    print(f'translate {text} to {target_text}')
    return target_text


if __name__ == '__main__':
    text = 'Beihang University'
    print(translate(text))
    print(translate_azure(text))
    print(translate_doubao(text))
