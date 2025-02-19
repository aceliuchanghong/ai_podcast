import os
from dotenv import load_dotenv
import logging
from termcolor import colored
import requests

load_dotenv()
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s-%(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def upload_wav2xyz(file_path, url, token):
    """
    上传音频文件到指定的 URL 以进行音频转文字。

    :param file_path: 音频文件路径
    :param url: 目标 URL, v1/audio/upload
    :return: 请求的响应对象
    """
    files = {"file": open(file_path, "rb")}
    response = requests.post(url, files=files)

    if response.status_code == 200:
        logger.info(colored(f"2.音频文件上传成功", "green"))
        return response
    else:
        logger.error(
            colored(f"2.音频文件上传失败-状态码:{response.status_code}", "green")
        )
        return None


if __name__ == "__main__":
    upload_wav2xyz()
