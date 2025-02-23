## AI_Podcast
AI播客

- [AI\_Podcast](#ai_podcast)
  - [实施步骤](#实施步骤)
  - [API文档](#api文档)
    - [音频生成部分api文档](#音频生成部分api文档)
  - [安装](#安装)


### 实施步骤
```
1. 获取每日热搜 或者 热点新闻
2. 由大模型生成 播音文案
3. tts模型生成 对话语音
4. 自动上传各个平台

podcast_server:
parse_got_list_api_bak(链接获取)==>jina_request(爬虫开始)==>get_sentense_list(播音文案)==>send_text_to_speech(音频)==>server(合并音频+存入表)

upload_func:
上传+存数据库+每次之前刷新code:upload_wav()==>upload_pic==>upload_task

main:
执行
```

upload_task
### API文档

包含音频生成server部分+上传部分

#### 音频生成部分api文档
```
# 单句 input-example
curl http://127.0.0.1:21500/v1/audio/speech \
  -H "Authorization: Bearer $podcast_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "kokoro-82M",
    "input": "Today is a wonderful day to build something people love!",
    "voice": "af_alloy"
  }'

# 单句 output-example
[
    {
        "title": "Today is a wonderful day to build something people love!",
        "file_path": "/root/mnt/data/llch/ai_podcast/no_git_oic/test/0d46386c7756d1983be4b83cff7492f3.wav",
        "detail": [
            {
                "speaker": "af_alloy",
                "text": "Today is a wonderful day to build something people love!",
                "trans_text": "今天是一个创造人们喜爱的事物的美好日子！",
                "time_span": "00:00:00-00:00:03",
            }
        ],
    }
]

# 参数解释:
1. 针对输入:当`model=kokoro-82M`,测试发送的是否服务成功. 当`model=podcast`,开始正式服务启动,其他均不成功
2. 针对输出:输出为list,每个list包含默认5个dict,每个dict是一个文章的实施,其包含(文章标题+文件路径+每一句音频细节)
   针对每一句细节(说话人+英文+翻译+时间轴段):
[
    {
        "speaker": "bella",
        "text": "Today is a wonderful day to build something people love!",
        "trans_text": "今天是一个创造人们喜爱的事物的美好日子！",
        "time_span": "00:00:00-00:00:03",
    },
    ...
]

# 定时任务 input-example
curl http://127.0.0.1:21500/v1/audio/speech \
  -H "Authorization: Bearer $podcast_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "podcast"
  }'

# 定时任务 output-example
[
    {
        "title": "Today is a wonderful day to build something people love!",
        "cover": "./no_git_oic/pic/36kr_4ea591c0149cc3029852cc3820111765.jpg",
        "file_path": "/root/mnt/data/llch/ai_podcast/no_git_oic/test/0d46386c7756d1983be4b83cff7492f3.wav",
        "detail": [
            {
                "speaker": "bella",
                "text": "Today is a wonderful day to build something people love!",
                "trans_text": "今天是一个创造人们喜爱的事物的美好日子！",
                "time_span": "00:00:00-00:00:03",
            },
            ...
        ],
    },
    ...
]

# voice
CHOICES = [
    "af_bella",  # 0
    "af_alloy",
    "af_aoede",
    "af_heart",
    "af_jessica",
    "af_kore",
    "af_nicole",  # 6
    "af_nova",
    "af_river",
    "af_sarah",
    "af_sky",
    "am_adam",  # 11
    "am_echo",  # 12
    "am_eric",
    "am_fenrir",
    "am_liam",
    "am_michael",
    "am_onyx",
    "am_puck",
    "am_santa",
    "bf_alice",
    "bf_emma",
    "bf_isabella",
    "bf_lily",
    "bm_daniel",
    "bm_fable",
    "bm_george",
    "bm_lewis",
    "ef_dora",
    "em_alex",
    "em_santa",
    "ff_siwis",
    "hf_alpha",
    "hf_beta",
    "hm_omega",
    "hm_psi",
    "if_sara",
    "im_nicola",
    "jf_alpha",
    "jf_gongitsune",
    "jf_nezumi",
    "jf_tebukuro",
    "jm_kumo",
    "pf_dora",
    "pm_alex",
    "pm_santa",
    "zf_xiaobei",
    "zf_xiaoni",
    "zf_xiaoxiao",
    "zf_xiaoyi",
    "zm_yunjian",
    "zm_yunxi",
    "zm_yunxia",
    "zm_yunyang",
]
```

### 安装 
```
# 设定环境变量 
~/.bashrc ==> export JINA_API_KEY=
~/.bashrc ==> export API_KEY=
~/.bashrc ==> export MOBILE_NUMBER=
source ~/.bashrc
apt-get install ffmpeg libavcodec-extra
git clone https://github.com/aceliuchanghong/ai_podcast
uv venv
source .venv/bin/activate
uv pip install .
uv run podcast_gen_server.py
uv run main_podcast_server.py
```
