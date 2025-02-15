# AI_Podcast
AI播客

- [AI\_Podcast](#ai_podcast)
  - [实施步骤](#实施步骤)
  - [API文档](#api文档)
  - [设定环境变量](#设定环境变量)


## 实施步骤
```
1. 获取每日热搜 或者 热点新闻
2. 由大模型生成 播音文案
3. tts模型生成 对话语音
4. 自动上传各个平台
```

## API文档
```
# input-example
curl http://127.0.0.1:21500/v1/audio/speech \
  -H "Authorization: Bearer $podcast_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "kokoro-82M",
    "input": "Today is a wonderful day to build something people love!",
    "voice": "bella"
  }'

# output-example
[
    {
        "title": "Today is a wonderful day to build something people love!",
        "file_path": "/root/mnt/data/llch/ai_podcast/no_git_oic/test/0d46386c7756d1983be4b83cff7492f3.wav",
        "detail": [
            {
                "speaker": "bella",
                "text": "Today is a wonderful day to build something people love!",
                "trans_text": "今天是一个创造人们喜爱的事物的美好日子！",
                "time_span": "00:00:00-00:00:03",
            }
        ],
    }
]

解释:
1.当`model=kokoro-82M`,测试发送的是否服务成功. 当`model=podcast`,开始正式服务启动,其他均不成功
2.输出为list,每个list为dict,每个dict包含 文章标题+文件路径+音频每一句话细节
其中针对每一句细节(说话人+英文+翻译+时间轴段):
[
    {
        "speaker": "bella",
        "text": "Today is a wonderful day to build something people love!",
        "trans_text": "今天是一个创造人们喜爱的事物的美好日子！",
        "time_span": "00:00:00-00:00:03",
    },
    ...
]
```

## 设定环境变量 
```
# 设定环境变量 
~/.bashrc ==> export JINA_API_KEY=
~/.bashrc ==> export API_KEY=
```
