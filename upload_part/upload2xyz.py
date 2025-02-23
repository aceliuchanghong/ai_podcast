import os
from dotenv import load_dotenv
import logging
from termcolor import colored
import sys
import time

load_dotenv()
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s-%(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")),
)

from upload_part.xyz.upload_xyz import upload_wav, upload_pic, upload_task
from client import generate_speech
from refresh_token import refersh_xyz
from ai_part.tts.kokoro_by_deepinfra import compute_mdhash_id


def process_audio_generation_and_upload(api_key, model, max_retries=2):
    """
    处理音频生成和上传的完整流程，带重试机制

    Args:
        api_key: API密钥
        model: 使用的模型
        max_retries: 最大重试次数
    """

    def try_upload(operation, *args, operation_name=""):
        retries = 0
        while retries < max_retries:
            try:
                access_token = refersh_xyz()
                operation(access_token, *args)
                return True
            except Exception as e:
                retries += 1
                logger.error(
                    colored(
                        f"错误 - {operation_name} 尝试 {retries}/{max_retries}: {str(e)}",
                        "red",
                    )
                )
                if retries == max_retries:
                    logger.error(
                        colored(f"达到最大重试次数，{operation_name}失败", "red")
                    )
                    raise Exception(f"多次尝试后{operation_name}仍失败")
                time.sleep(2**retries)  # 指数退避延迟

    # 1. 生成音频文件
    logger.info(colored(f"1. 开始生成文件...", "green"))
    gen_wav_detail_list = generate_speech(api_key, model)
    wav_file_path = gen_wav_detail_list[0]["file_path"]
    cover_file_path = gen_wav_detail_list[0]["cover"]
    title = gen_wav_detail_list[0]["title"]
    file_md5_code = compute_mdhash_id(title)

    # 2. 上传wav文件
    logger.info(colored(f"2. 开始上传wav...", "green"))
    try_upload(upload_wav, wav_file_path, operation_name="上传wav")

    # 3. 上传封面
    logger.info(colored(f"3. 开始上传封面...", "green"))
    try_upload(upload_pic, cover_file_path, wav_file_path, operation_name="上传封面")

    # 4. 上传任务
    logger.info(colored(f"4. 开始上传任务...", "green"))
    try_upload(
        upload_task, gen_wav_detail_list[0], file_md5_code, operation_name="上传任务"
    )

    # 5. 完成提示
    logger.info(colored(f"5. upload done", "green"))

    return gen_wav_detail_list


if __name__ == "__main__":
    """
    python upload_part/upload2xyz.py
    """
    api_key = os.getenv("podcast_api_key")
    model = "podcast"

    for i in range(1):
        process_audio_generation_and_upload(api_key, model)
