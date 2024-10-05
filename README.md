Python运行的时候报依赖不存在的错误就手动pip install一下即可

author.py
自动获取当前查询分页中所有文章的作者信息，包括作者名字、单位
由于每个分页最多有50条记录，因此每运行一次最多获取50条，也可以优化一下代码，能够自动切换到下一页，不过感觉50条一次已经够了
由于查询次数较多，因此有可能被网页拦截，需要手动输入验证码，因此在运行的时候要注意观察验证码窗口是否弹出，如果弹出后没及时处理，那么中途的一些作者学校就会被跳过
可以根据自己的网络适当调整代码中的超时时间
在刚启动的时候，会提示你处理验证码，在处理完成之后，在控制台输入任意字符，然后回车，程序会继续运行

author_title.py
自动查询excel中作者的头衔，需要手动将作者名字粘贴到excel中，然后运行代码即可

journal.py
自动根据data.txt中的所有期刊名字获取其中科院分级，如果无法查询分区会在结果中提示，然后将其按照在文件中的顺序粘贴到excel中即可
部分结果可能会有误差，例如格式不完全匹配等，需要人工核对一下

下面的配置存放在settings.py中

该代码使用了kimi大模型，需要手动获得api key后才能使用
api key获取地址：https://platform.moonshot.cn/console/api-keys

翻译功能：可以用豆包大模型，或者腾讯云来进行翻译，默认为豆包大模型，若需要使用腾讯翻译，则需要在author.py中将translate_doubao改为translate
配置说明
字节的豆包lite-4k大模型来进行翻译，需要手动获得api key后才能使用
https://console.volcengine.com/ark/region:ark+cn-beijing/model?vendor=Bytedance&view=LIST_VIEW
然后在“在线推理”中创建一个新的推理接入点

腾讯云的翻译功能，需要手动获得api key和api secret后才能使用
api key和api secret获取地址：https://console.cloud.tencent.com/cam/capi
然后还需要在控制台中启用机器翻译功能
https://console.cloud.tencent.com/tmt

