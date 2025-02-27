import requests
import os
from dotenv import load_dotenv
import logging
from termcolor import colored
import json
import math

load_dotenv()
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s-%(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def send_login_request(mobile_phone_number, url, area_code="+86") -> bool:
    """
    发送 POST 请求到指定的 URL 以进行 SMS 登录。

    :param area_code: 区号，例如 "+86"
    :param mobile_phone_number: 手机号码，例如 "xxx"
    :param url: 目标 URL, v1/auth/send-code
    :return: 请求的响应对象
    """
    data = {"areaCode": area_code, "mobilePhoneNumber": mobile_phone_number}
    response = requests.post(url, json=data)

    if response.status_code == 200:
        # logger.info(colored(f"短信验证码请求成功", "green"))
        return True
    else:
        logger.error(colored(f"1.验证码失败-状态码:{response.status_code}", "green"))
        return False


def complete_login_with_verify_code(
    mobile_phone_number, url, verify_code, area_code="+86"
):
    """
    发送 POST 请求到指定的 URL 以完成登录，包含验证码。

    :param area_code: 区号，例如 "+86"
    :param mobile_phone_number: 手机号码，例如 "xx"
    :param verify_code: 验证码，例如 "6483"
    :param url: 目标 URL /v1/auth/login-with-sms
    :return: 请求的响应对象
    """
    # 构建请求数据
    data = {
        "areaCode": area_code,
        "mobilePhoneNumber": mobile_phone_number,
        "verifyCode": verify_code,
    }

    response = requests.post(url, json=data)
    if response.status_code == 200:
        # logger.info(colored(f"2.登录请求成功", "green"))
        accessToken = response.headers.get("x-jike-access-token")
        refreshToken = response.headers.get("x-jike-refresh-token")
        return accessToken, refreshToken
    else:
        logger.error(colored(f"2.登录请求失败-状态码:{response.status_code}", "green"))
        return


def get_url_response(url, accessToken):
    """
    :return: 请求的响应对象
    """
    headers = {"x-jike-access-token": accessToken}

    response = requests.get(url, headers=headers)

    return response


def post_response(url, authorization, data=None):

    headers = {"authorization": authorization}

    response = requests.post(url, headers=headers, json=data)

    return response


def refresh_tokens(url, accessToken, refreshToken):
    headers = {
        "x-jike-access-token": accessToken,
        "x-jike-refresh-token": refreshToken,
    }

    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        accessToken = response.headers.get("x-jike-access-token")
        refreshToken = response.headers.get("x-jike-refresh-token")
        return accessToken, refreshToken
    else:
        logger.error(colored(f"Token刷新失败-code: {response.status_code}", "red"))
        return


# 示例调用
if __name__ == "__main__":
    # python upload_part/xyz/cookie_getter.py
    mobile_phone_number = os.getenv("MOBILE_NUMBER")
    send_login_request_url = os.getenv("xyz_send_code_url")
    complete_login_url = os.getenv("xyz_complete_login_url")
    check_url = os.getenv("xyz_check_url")
    refresh_url = os.getenv("xyz_refresh_url")

    # response = send_login_request(mobile_phone_number, send_login_request_url)

    # accessToken, refreshToken = complete_login_with_verify_code(
    #     mobile_phone_number, complete_login_url, verify_code
    # )
    # logger.info(
    #     colored(f"accessToken:{accessToken}\nrefreshToken:{refreshToken}", "green")
    # )

    token_file = "no_git_oic/xyz_token.json"
    with open(token_file, "r") as f:
        tokens = json.load(f)
        access_token = tokens.get("accessToken")
        refresh_token = tokens.get("refreshToken")
    logger.info(
        colored(
            f"\naccessToken:{access_token}\nrefreshToken:{refresh_token}",
            "green",
        )
    )

    # check
    # response = get_url_response(check_url, access_token)
    # print(f"{response.json()}")

    # ready to upload 获取token QTmM-Cgln
    ready_upload_url = os.getenv("xyz_ready_upload_url")
    response = get_url_response(ready_upload_url, access_token)
    print(f"{response.json()}")

    token = response.json()["token"]
    token_ak = response.json()["token"].split(":")[0]
    # 似乎没什么用
    # ready_upload_url2 = os.getenv("xyz_ready_upload_url2")
    # response = get_url_response(ready_upload_url2.replace("?ak=","?ak=" + token_ak), access_token)
    # print(f"{response.json()}")

    # 获取 uploadId
    upload_url = os.getenv("xyz_upload_url")
    response = post_response(upload_url, "UpToken " + token)
    print(f"{response.json()}")

    uploadId = response.json()["uploadId"]
    file_path = "no_git_oic/fcd32c7027c455e28b1879fc719df0f8.wav"
    # 计算该文件需要多少次put
    chunk_size = 2 * 1024 * 1024
    file_size = os.path.getsize(file_path)
    num_chunks = math.ceil(file_size / chunk_size)
    print(f"文件大小: {file_size} 字节")
    print(f"分片大小: {chunk_size} 字节")
    print(f"总分片数: {num_chunks}")
    parts = []
    with open(file_path, "rb") as file:
        for i in range(num_chunks):
            # 计算当前分片的偏移量和大小
            offset = i * chunk_size
            bytes_to_read = min(chunk_size, file_size - offset)
            # 最后一个分片可能小于 chunk_size
            # 读取分片数据
            file.seek(offset)
            chunk_data = file.read(bytes_to_read)
            # 构造当前分片的 URL
            current_url = upload_url + "/" + uploadId + "/" + str(i + 1)
            logger.info(colored(f"分片 {i + 1}/{num_chunks} 开始上传...", "green"))
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
                print(f"分片 {i + 1}/{num_chunks} 上传失败: {e}")
                break
    # 合并post
    last_wav_post_dict = {"parts": parts, "fname": os.path.basename(file_path)}
    response = post_response(
        upload_url + "/" + uploadId, "UpToken " + token, last_wav_post_dict
    )
    print(f"{response.json()}")

    all_create = {}
    all_create["pid"] = "67b1b39b675981bb8243a940"
    all_create["title"] = os.path.basename(file_path).replace(".wav", "")
    all_create["file"] = response.json()["file"]

    create_url = os.getenv("xyz_create_url")
    # 最后页面create
    response = requests.post(
        create_url, headers={"x-jike-access-token": access_token}, json=all_create
    )
    print(f"{response.json()}")

    # logger.info(colored(f"{refresh_url}", "green"))
    # accessToken, refreshToken = refresh_tokens(refresh_url, access_token, refresh_token)
    # logger.info(
    #     colored(
    #         f"\naccessToken:{accessToken}\nrefreshToken:{refreshToken}",
    #         "green",
    #     )
    # )
