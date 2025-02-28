import os
from dotenv import load_dotenv
import logging
from termcolor import colored
import time
import random

load_dotenv()
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s-%(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

from upload_part.upload2xyz import process_audio_generation_and_upload


def main(wait_hour):
    # 获取API key
    api_key = os.getenv("podcast_api_key")
    model = "podcast"
    wait_time_1 = wait_hour * 60 * 60
    wait_time_2 = wait_hour * 60 * 60 + 5
    while True:
        try:
            # 执行音频生成和上传
            logger.info(
                colored(
                    f"开始执行音频生成和上传: {time.strftime('%Y-%m-%d %H:%M:%S')}",
                    "green",
                )
            )
            process_audio_generation_and_upload(api_key, model)
            logger.info(
                colored(f"完成执行: {time.strftime('%Y-%m-%d %H:%M:%S')}", "green")
            )

            # 随机等待 wait_time - wait_time+5 分钟（转换为秒）
            wait_time = random.randint(wait_time_1, wait_time_2)
            print(f"等待 {wait_time//60} 分钟 {wait_time%60} 秒...")
            time.sleep(wait_time)

        except Exception as e:
            logger.error(colored(f"发生错误: {str(e)}", "red"))
            print(f"等待60分钟...")
            time.sleep(60 * 60)


if __name__ == "__main__":
    """
    python main_podcast_server.py
    nohup python main_podcast_server.py > no_git_oic/main_podcast_server.log 2>&1 &
    ps -ef | grep main_podcast_server
    """
    wait_hour = int(os.getenv("WAIT_HOUR", 3))
    main(wait_hour)
