import requests
import os
from dotenv import load_dotenv
import logging
from termcolor import colored
import json

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
    response = get_url_response(check_url, access_token)
    print(f"{response.json()}")

    # logger.info(colored(f"{refresh_url}", "green"))
    # accessToken, refreshToken = refresh_tokens(refresh_url, access_token, refresh_token)
    # logger.info(
    #     colored(
    #         f"\naccessToken:{accessToken}\nrefreshToken:{refreshToken}",
    #         "green",
    #     )
    # )
