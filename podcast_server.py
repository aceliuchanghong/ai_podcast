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

load_dotenv()
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s-%(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

from ai_part.tts.kokoro_by_deepinfra import send_text_to_speech
from ai_part.crawler.crawler_by_jina import jina_request
from ai_part.utils.tools import parse_got_list_api, trans_sentense


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
        logger.info(colored(f"\nrequest recieved suc:{request}", "green"))
        # 单纯测试
        if request["model"] == "kokoro-82M":
            output_file = send_text_to_speech(
                text=request["input"], output_file_destination="no_git_oic/test"
            )
            current_dir = os.path.dirname(os.path.abspath(__file__))
            output_path = os.path.join(current_dir, output_file)

            duration = get_wav_duration(output_path)
            time_span = format_time_span(duration)
            return [
                {
                    "title": request["input"],
                    "file_path": output_path,
                    "detail": [
                        {
                            "speaker": "bella",
                            "text": request["input"],
                            "trans_text": trans_sentense(
                                request["input"], self.client, "中文"
                            ),
                            "time_span": "00:00:00-" + time_span,
                        },
                    ],
                }
            ]
        # 如果是podcast 正式启动服务
        if request["model"] == "podcast":
            # 获取待获取文章的list
            article_list = parse_got_list_api(
                os.getenv("podcast_site_url"),
                int(os.getenv("podcast_article_post_nums")),
            )
            logger.info(colored(f"文章列表:{article_list}", "green"))
            today_article_list = []
            for article in article_list:
                title = article["title"]
                url = article["url"]
                # 获取文章内容
                today_article = jina_request(
                    url=url,
                    authorization_token=os.getenv("JINA_API_KEY"),
                )
                today_article_list.append(today_article)
            # 2.获取文案
            # 3.获取音频
            return today_article_list
        else:
            return "model not found"

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
    api = PodcastServer()
    server = ls.LitServer(api, api_path="/v1/audio/speech")
    server.run(port=int(os.getenv("podcast_port", 21500)))
