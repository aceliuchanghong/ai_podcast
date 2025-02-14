import requests
from typing import Union
import os


def jina_request(url: str, authorization_token: str) -> Union[requests.Response, str]:
    """
    发送GET请求到Jina API。

    参数:
    url (str): 相对路径,将被附加到Jina API的基础URL上。
    authorization_token (str): 授权令牌，用于验证请求。

    返回:
    Union[requests.Response, str]: 请求的响应对象，或者在发生错误时返回错误信息字符串。

    异常:
    - ValueError: 如果输入的URL或授权令牌为空。
    - requests.exceptions.RequestException: 如果请求过程中发生网络错误或其他异常。
    """
    if not url or not authorization_token:
        raise ValueError("URL和授权令牌不能为空")

    full_url = os.getenv("JINA_URL") + url

    headers = {"Authorization": f"Bearer {authorization_token}"}

    try:
        response = requests.get(full_url, headers=headers)
        response.raise_for_status()  # 如果响应状态码不是200，会抛出HTTPError
        return response.text
    except requests.exceptions.RequestException as e:
        return f"请求失败: {e}"


if __name__ == "__main__":
    """
    python ai_part/crawler/crawler_by_jina.py
    ~/.bashrc ==> JINA_API_KEY
    """
    key = os.getenv("JINA_API_KEY")
    url = "https://mp.weixin.qq.com/s/DOI3-TLLhNTMpLWEtB7X2g"
    response = jina_request(url, key)
    print(response)
