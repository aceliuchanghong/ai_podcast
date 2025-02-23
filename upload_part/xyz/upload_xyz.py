import os
from dotenv import load_dotenv
import logging
from termcolor import colored
import sys

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
    os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../")),
)

from upload_part.xyz.cookie_getter import *
from ai_part.utils.sql_sentence import *
from ai_part.utils.check_db import execute_sqlite_sql
from ai_part.utils.parse_xyz import parse_json2xyz


def upload_wav(access_token, file_path) -> bool:
    # 获取 upload token
    ready_upload_url = os.getenv("xyz_ready_upload_url")
    token_response = get_url_response(ready_upload_url, access_token)
    token = token_response.json()["token"]
    logger.info(colored(f"1. upload token:{token[:10]}", "green"))

    # 获取 uploadId
    upload_url = os.getenv("xyz_upload_url")
    uploadId_response = post_response(upload_url, "UpToken " + token)
    uploadId = uploadId_response.json()["uploadId"]
    logger.info(colored(f"2. uploadId:{uploadId}", "green"))

    # 计算该文件需要多少次put
    chunk_size = int(os.getenv("chunk_size"))
    file_size = os.path.getsize(file_path)
    num_chunks = math.ceil(file_size / chunk_size)
    logger.info(colored(f"3. 总分片数: {num_chunks}", "green"))

    # 准备上传分片
    parts = []
    all_create = {}
    with open(file_path, "rb") as file:
        for i in range(num_chunks):
            offset = i * chunk_size
            bytes_to_read = min(chunk_size, file_size - offset)
            file.seek(offset)
            chunk_data = file.read(bytes_to_read)
            # 构造当前分片的 URL
            current_url = upload_url + "/" + uploadId + "/" + str(i + 1)
            try:
                # 发送 PUT 请求
                response = requests.put(
                    current_url,
                    data=chunk_data,
                    headers={"authorization": "UpToken " + token},
                )
                if response.status_code == 200:
                    logger.info(colored(f"分片 {i + 1}/{num_chunks} 上传成功", "green"))
                    ans_dict = {"etag": response.json()["etag"], "partNumber": i + 1}
                    parts.append(ans_dict)
            except requests.exceptions.RequestException as e:
                logger.error(colored(f"分片 {i + 1}/{num_chunks} 上传失败: {e}", "red"))
                return False
    logger.info(colored(f"4. 全部上传成功", "green"))

    # 合并post信息
    last_wav_post_dict = {"parts": parts, "fname": os.path.basename(file_path)}
    last_wav_post_response = post_response(
        upload_url + "/" + uploadId, "UpToken " + token, last_wav_post_dict
    )
    all_create["pid"] = os.getenv("bella_pid")
    all_create["title"] = os.path.basename(file_path).replace(".wav", "")
    all_create["file"] = last_wav_post_response.json()["file"]
    logger.info(colored(f"5. 合并post信息成功", "green"))

    # 最后页面create
    create_url = os.getenv("xyz_create_url")
    response = requests.post(
        create_url, headers={"x-jike-access-token": access_token}, json=all_create
    )
    logger.info(colored(f"6. create 任务成功", "green"))
    # 数据库更新
    execute_sqlite_sql(update_detail_wav_sql, (file_path,))
    logger.info(colored(f"7. 数据库更新成功", "green"))
    return True


def upload_pic(access_token, img_file_path, wav_file_path) -> bool:
    # 获取 upload token
    ready_upload_url = os.getenv("xyz_ready_upload_url2")
    token_response = get_url_response(ready_upload_url, access_token)
    token = token_response.json()["token"]
    logger.info(colored(f"1. upload token:{token[:10]}", "green"))

    # 准备上传
    upload_url = os.getenv("xyz_upload_url2")
    with open(img_file_path, "rb") as file:
        img_data = file.read()
        # 如果大于10MB,返回失败
        if len(img_data) >= 10 * 1024 * 1024:
            logger.error(colored(f"图片大于等于10MB", "red"))
            return False
        data = {"token": token, "fname": os.path.basename(img_file_path)}
        files = {
            "file": (
                os.path.basename(img_file_path),
                img_data,
                "image/jpeg",
            )
        }
        # Send the POST request
        image_post_response = requests.post(upload_url, data=data, files=files)
        if image_post_response.status_code != 200:
            logger.error(colored(f"图片上传失败:{image_post_response}", "red"))
            return False
        logger.info(colored(f"2. 图片上传成功", "green"))

    # 最后页面create
    image_post_response = image_post_response.json()
    all_create = {}
    all_create["pid"] = os.getenv("bella_pid")
    all_create["title"] = os.path.basename(img_file_path).split(".")[0]
    all_create["file"] = image_post_response["file"]

    create_url = os.getenv("xyz_create_url")
    response = requests.post(
        create_url, headers={"x-jike-access-token": access_token}, json=all_create
    )
    logger.info(colored(f"3. create 任务成功", "green"))
    # 数据库更新
    execute_sqlite_sql(update_detail_pic_sql, (wav_file_path,))
    logger.info(colored(f"4. 数据库更新成功", "green"))
    return True


def upload_task(access_token, task_notes_dict, file_md5_code) -> bool:
    logger.info(colored(f"1. 开始上传...", "green"))

    get_list_url = os.getenv("xyz_list_url")
    create_task_url = os.getenv("xyz_task_create")
    wav_dict_payload = {
        "skip": 0,
        "pid": os.getenv("bella_pid"),
        "limit": 1000,
        "type": "AUDIO",
    }
    pic_dict_payload = {
        "skip": 0,
        "pid": os.getenv("bella_pid"),
        "limit": 1000,
        "type": "IMAGE",
    }
    # 获取已上传文件列表
    headers = {"x-jike-access-token": access_token}
    try:
        wav_list = requests.post(get_list_url, headers=headers, json=wav_dict_payload)
        pic_list = requests.post(get_list_url, headers=headers, json=pic_dict_payload)
        logger.info(
            colored(
                f"2. total_wav:{len(wav_list.json()["data"])},total_pic:{len(pic_list.json()["data"])}, 网站选中文件成功",
                "green",
            )
        )
    except requests.exceptions.RequestException as e:
        logger.error(colored(f"2. 网站获取文件失败:{e}", "red"))
        return False

    # 准备上传
    title = task_notes_dict["title"]
    shownotes = parse_json2xyz(task_notes_dict["detail"])

    # 核心-选择文件
    for index, wav_name in enumerate(wav_list.json()["data"]):
        if (
            os.path.basename(task_notes_dict["file_path"]).split(".")[0]
            == wav_name["title"]
        ):
            audioFile = wav_list.json()["data"][index]["audioFile"]
            break

    for index, pic_name in enumerate(pic_list.json()["data"]):
        if (
            os.path.basename(task_notes_dict["cover"]).split(".")[0]
            == pic_name["title"]
        ):
            image = pic_list.json()["data"][index]["imageFile"]
            break

    if audioFile is None:
        raise UnboundLocalError("audioFile not found")
    if image is None:
        raise UnboundLocalError("image not found")

    max_index_list = execute_sqlite_sql(select_max_index_detail_info_sql)
    if len(max_index_list) == 0 or max_index_list[0][0] is None:
        max_index = 0
    else:
        max_index = int(max_index_list[0][0])

    task_payload = {
        "title": f"【{str(max_index + 1)}】" + title,
        "shownotes": shownotes
        + "<p>   </p><p>   </p><p>"
        + os.getenv("tail")
        + "\n"
        + "</p>",
        "pid": os.getenv("bella_pid"),
        "audioFile": audioFile,
        "image": image,
    }

    response = requests.post(create_task_url, headers=headers, json=task_payload)
    if response.status_code != 200:
        logger.error(colored(f"3. 最终任务上传失败:{response}", "red"))
        return False
    logger.info(colored(f"3. create 任务成功", "green"))

    execute_sqlite_sql(update_detail_task_sql, (file_md5_code,))
    logger.info(colored(f"4. 数据库更新成功", "green"))
    return True


if __name__ == "__main__":
    # python upload_part/xyz/upload_xyz.py
    token_file = "no_git_oic/xyz_token.json"
    with open(token_file, "r") as f:
        tokens = json.load(f)
        access_token = tokens.get("accessToken")
    # logger.info(colored(f"\naccess:{access_token}", "green"))

    # wav_file_path = "no_git_oic/30a987b14288d08b697d1b996a3929dc.wav"
    # upload_wav(access_token, wav_file_path)

    # img_file_path = "no_git_oic/pics/friru.jpg"
    # upload_pic(access_token, img_file_path, wav_file_path)

    test_task_dict = {
        "title": "1",
        "detail": "<p>1</p>",
        "file_path": "no_git_oic/30a987b14288d08b697d1b996a3929dc.wav",
        "cover": "no_git_oic/pics/friru.jpg",
    }
    upload_task(access_token, test_task_dict)
