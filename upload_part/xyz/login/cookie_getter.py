import requests
import os
from dotenv import load_dotenv
import logging
from termcolor import colored

load_dotenv()
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s-%(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# headers = {
#     "Accept": "application/json, text/plain, */*",
#     "Accept-Encoding": "gzip, deflate, br, zstd",
#     "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
#     "Content-Length": "72",
#     "Content-Type": "application/json;charset=UTF-8",
#     "Priority": "u=1, i",
#     "Sec-CH-UA": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
#     "Sec-CH-UA-Mobile": "?0",
#     "Sec-CH-UA-Platform": '"Windows"',
#     "Sec-Fetch-Dest": "empty",
#     "Sec-Fetch-Mode": "cors",
#     "Sec-Fetch-Site": "same-origin",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
# }


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
        logger.info(colored(f"1.短信验证码请求成功", "green"))
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
        logger.info(colored(f"2.登录请求成功", "green"))
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
    if response.status_code == 200:
        return response
    else:
        raise Exception(f"401失败-cookie过期: {response.status_code}")


def post_url_response(url, accessToken, refreshToken=None):
    """
    :return: 请求的响应对象
    """
    if refreshToken:
        headers = {
            "x-jike-access-token": accessToken,
            "x-jike-refresh-token": refreshToken,
        }
    else:
        headers = {"x-jike-access-token": accessToken}

    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return response
    else:
        raise Exception(f"401失败-cookie过期: {response.status_code}")


# 示例调用
if __name__ == "__main__":
    # python upload_part/xyz/login/cookie_getter.py
    mobile_phone_number = os.getenv("MOBILE_NUMBER")
    send_login_request_url = os.getenv("xyz_send_code_url")
    complete_login_url = os.getenv("xyz_complete_login_url")
    check_url = os.getenv("xyz_check_url")
    verify_code = "2670"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiclN2XC9EaWxDXC9NSUdVcExHWHpTK1U1NGJaVFNnOVwvMEpWdnBPQ09KTGgyd1IzTWN5XC9cL2VJb20yRkJicW54Q0k1bzlxakk5OGorQ1g2NFA5cHg0dUFwZFNxRFZwd2lEczZwUWxmVmJnK0lBcFk0VnJPT2xsd3J2VFBLcjNreDJYRjE0M0lGSWlxRXd6ZU4rRTdKcVBzMFVzam51N0p4UFN6amVRREhPXC9Ib3ZhVjkyTm5NS25Fd3NxSnFndUFmMk5SZ01sOWFpeVZDN0ZpUVpjU0V1a0hxUWpTMFY1WEtGM3RvZU51M3BSRkk5OWZOdGhHcE5pUWsydnBEaHBPMjBVbUN4SFFZYjVSZXhBQjQzZHdHanZ5NXp5VUxQcmoyZW1RVkphSEFRT1VnOFR5cDdoYU92bnlIWWlDK3BzUVk4WnJUR0xmSlNEN1VNWE94Q3hNRGduQWVnY2dDWVwvSnFXeXQzODNJMjNnOVRlYz0iLCJ2IjozLCJpdiI6InJQNit3TFNtVHMxdStFV3ZNMGtWeWc9PSIsImlhdCI6MTczOTkyNzI4Ni4xNDF9._5QhApeW89mFHju6tcm2d5tqg8evJ16uZzqYXvY7Cxw"

    # response = send_login_request(mobile_phone_number, send_login_request_url)

    # accessToken, refreshToken = complete_login_with_verify_code(
    #     mobile_phone_number, complete_login_url, verify_code
    # )
    # logger.info(
    #     colored(f"accessToken:{accessToken}\nrefreshToken:{refreshToken}", "green")
    # )

    response = get_url_response(check_url, token)
    print(response.json())
