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
from ai_part.utils.sql_sentence import *
from ai_part.utils.check_db import execute_sqlite_sql


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
                result = operation(access_token, *args)
                if not result:  # 检查返回值是否为False
                    raise ValueError(f"{operation_name}返回False")
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
                    raise Exception(f"多次尝试后{operation_name}仍失败: {str(e)}")
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
    if execute_sqlite_sql(select_already_up_wav_info_sql, (wav_file_path,))[0][0] != 1:
        if not try_upload(upload_wav, wav_file_path, operation_name="上传wav"):
            raise ValueError("WAV文件上传失败")

    # 3. 上传封面
    logger.info(colored(f"3. 开始上传封面...", "green"))
    if execute_sqlite_sql(select_already_up_pic_info_sql, (wav_file_path,))[0][0] != 1:
        if not try_upload(
            upload_pic, cover_file_path, wav_file_path, operation_name="上传封面"
        ):
            raise ValueError("封面上传失败")

    # 4. 上传任务
    logger.info(colored(f"4. 开始上传任务...", "green"))
    if not try_upload(
        upload_task, gen_wav_detail_list[0], file_md5_code, operation_name="上传任务"
    ):
        raise ValueError("任务上传失败")

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
