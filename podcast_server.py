import os
from dotenv import load_dotenv
import logging
from termcolor import colored
import litserve as ls
from openai import OpenAI
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import wave
from datetime import timedelta, datetime
from pydub import AudioSegment
import json
import time

load_dotenv()
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s-%(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

from ai_part.tts.kokoro_by_deepinfra import send_text_to_speech, compute_mdhash_id
from ai_part.crawler.crawler_by_jina import jina_request
from ai_part.utils.tools import (
    parse_got_list_api_bak,
    trans_sentense,
    get_sentense_list,
)
from ai_part.utils.sql_sentence import *
from ai_part.utils.check_db import execute_sqlite_sql


def get_wav_duration(file_path):
    with wave.open(file_path, "rb") as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        duration = frames / float(rate)
        return duration


def format_time_span(duration, last_duration_end_time_str="00:00:00"):
    # 将 last_duration_end_time_str 转换为 timedelta 对象
    if last_duration_end_time_str != "00:00:00":
        last_duration_end_time = datetime.strptime(
            last_duration_end_time_str, "%H:%M:%S"
        )
        last_duration_timedelta = timedelta(
            hours=last_duration_end_time.hour,
            minutes=last_duration_end_time.minute,
            seconds=last_duration_end_time.second,
        )
        end_time = timedelta(seconds=duration) + last_duration_timedelta
    else:
        end_time = timedelta(seconds=duration)

    hours, remainder = divmod(end_time.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    end_time_str = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    return end_time_str


class PodcastServer(ls.LitAPI):
    def setup(self, device):
        self.server_name = "PodcastServer"
        self.client = OpenAI(
            api_key=os.getenv("API_KEY"), base_url=os.getenv("BASE_URL")
        )

    def decode_request(self, request):
        logger.info(colored(f"\n\n\n\nrequest recieved suc:{request}", "green"))
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 单纯测试
        if request["model"] == "kokoro-82M":
            output_file = send_text_to_speech(
                text=request["input"],
                preset_voice_num=request["voice"],
                output_file_destination="no_git_oic/test",
            )
            output_path = os.path.join(current_dir, output_file)
            duration = get_wav_duration(output_path)
            time_span = format_time_span(duration)
            return [
                {
                    "title": request["input"],
                    "file_path": output_path,
                    "detail": [
                        {
                            "speaker": request["voice"],
                            "text": request["input"],
                            "trans_text": trans_sentense(
                                request["input"], self.client, "Chinese"
                            ),
                            "time_span": "00:00:00-" + time_span,
                        },
                    ],
                }
            ]
        # 如果是podcast 正式启动服务
        if request["model"] == "podcast":
            start_time = time.time()
            # 获取待获取文章的list
            article_list = parse_got_list_api_bak(
                os.getenv("bak_podcast_site_url"),
                int(os.getenv("podcast_article_post_nums")),
            )
            logger.info(colored(f"1.获取文章列表成功,文章列表:{article_list}", "green"))
            today_article_list = []
            for article in article_list:
                article_info = {}
                # 获取文章标题
                article_info["title"] = article["title"]
                article_info["detail"] = []
                article_info["file_path"] = "init"

                article_code = compute_mdhash_id(article["title"])
                # 获取文章内容
                logger.info(colored(f"2.爬虫开始获取文章", "green"))
                today_article_content = jina_request(
                    url=article["url"],
                    authorization_token=os.getenv("JINA_API_KEY"),
                )
                logger.info(colored(f"3.开始获取文章剧本", "green"))
                # 获取剧本
                script_list = get_sentense_list(today_article_content, self.client)
                if len(script_list) <= 2:
                    raise ValueError(
                        f"{article["url"]}:剧本内容为空\narticle:{article}"
                    )
                for script in script_list:
                    print(f"{script}")
                # 获取音频
                logger.info(colored(f"4.开始获取音频...", "green"))
                gen_wav_list = []
                for script in script_list:
                    if script[0].lower() == "bella":
                        preset_voice_num = 0
                    elif script[0].lower() == "adam":
                        preset_voice_num = 12
                    else:
                        raise ValueError(f"speaker:{script[0]} not in [bella,adam]")
                    audio_path = send_text_to_speech(
                        text=script[1],
                        preset_voice_num=preset_voice_num,
                        output_file_destination="no_git_oic/wav/" + article_code,
                    )
                    trans = trans_sentense(script[1], self.client, "Chinese")
                    gen_wav_list.append((script[0], script[1], audio_path, trans))
                # logger.info(colored(f"{gen_wav_list}", "green"))

                # 合并音频 并且输出结果 list
                last_duration_end_time_str = "00:00:00"
                final_output_path = os.path.join(
                    current_dir, "no_git_oic/wav/" + article_code + ".wav"
                )
                if os.path.exists(final_output_path):
                    os.remove(final_output_path)
                combined_audio = AudioSegment.silent(duration=0)

                for gen_wav in gen_wav_list:
                    """
                    [('Adam', "Hey Bella, have you heard about that?", 'no_git_oic/cac9a94.wav', '嘿，贝拉，你听说了吗？'),...]
                    """
                    audio_segment = AudioSegment.from_wav(gen_wav[2])
                    combined_audio += audio_segment

                    duration = get_wav_duration(gen_wav[2])
                    time_span = format_time_span(duration, last_duration_end_time_str)
                    article_info_detail_info = {}
                    article_info_detail_info["speaker"] = gen_wav[0]
                    article_info_detail_info["text"] = gen_wav[1]
                    article_info_detail_info["trans_text"] = gen_wav[3]
                    article_info_detail_info["time_span"] = (
                        last_duration_end_time_str + "-" + time_span
                    )
                    last_duration_end_time_str = time_span
                    article_info["detail"].append(article_info_detail_info)

                combined_audio.export(final_output_path, format="wav")
                article_info["file_path"] = final_output_path
                article_info["cover"] = os.path.join(current_dir, article["cover"])
                today_article_list.append(article_info)

                max_index_list = execute_sqlite_sql(select_max_index_detail_info_sql)
                if len(max_index_list) == 0 or max_index_list[0][0] is None:
                    max_index = 0
                else:
                    max_index = int(max_index_list[0][0])
                # 存入数据库
                execute_sqlite_sql(
                    insert_detail_info_sql,
                    (
                        article_code,
                        max_index + 1,
                        json.dumps(article_info["detail"], ensure_ascii=False),
                        final_output_path,
                        article_info["cover"],
                        "",
                        "",
                        "",
                    ),
                )
                execute_sqlite_sql(
                    insert_basic_info_sql,
                    (article["title"], article["url"], article_code, ""),
                )
                logger.info(colored("5.合并音频成功", "green"))

            logger.info(colored(f"6. 输出存档:\n{today_article_list}", "green"))

            end_time = time.time()
            elapsed_time = end_time - start_time
            logger.info(colored(f"7. 此播客生成共耗时: {elapsed_time:.2f}秒", "green"))

            return today_article_list
        else:
            raise ValueError("只支持podcast和kokoro-82M")

    def predict(self, inputs):
        output = inputs
        return output

    def encode_response(self, output):
        return output

    def authorize(self, auth: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        if auth.scheme != "Bearer" or auth.credentials != os.getenv("podcast_api_key"):
            raise HTTPException(status_code=401, detail="Authorization Failed")


if __name__ == "__main__":
    """
    python podcast_server.py
    nohup python podcast_server.py > no_git_oic/podcast_server.log 2>&1 &
    """
    execute_sqlite_sql(create_basic_table_sql)
    execute_sqlite_sql(create_detail_table_sql)
    api = PodcastServer()
    server = ls.LitServer(api, api_path="/v1/audio/speech")
    server.run(port=int(os.getenv("podcast_port", 21500)))
