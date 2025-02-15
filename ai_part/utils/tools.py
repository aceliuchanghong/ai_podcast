import os
from dotenv import load_dotenv
import logging
from termcolor import colored
import requests
from openai import OpenAI
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

from ai_part.utils.get_json import parse_and_check_json_markdown


def parse_got_list_api(url: str, nums: int = 5) -> list:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            logger.info(colored(f"成功获取数据: {data['data'][:nums]}", "green"))
            return data["data"][:nums]
        else:
            logger.error(f"请求失败，状态码：{response.status_code}, URL: {url}")
            print(f"请求失败，状态码：{response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        logger.error(f"请求异常: {e}, URL: {url}")
        print(f"请求异常: {e}")
        return []


def trans_sentense(sentense: str, client: OpenAI, language: str = "英文") -> str:
    if language not in ["中文", "英文"]:
        raise ValueError("只支持中文和英文翻译")
    prompt = f"请将以下内容翻译成{language},以json格式返回:\n{sentense}\nexample:\n{{'translate_result': '翻译后的内容'}}"
    try:
        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "qwen2.5:7b-instruct-fp16"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        logger.info(
            colored(f"llm-output:{response.choices[0].message.content}", "green")
        )
        trans = parse_and_check_json_markdown(
            response.choices[0].message.content, ["translate_result"]
        )
        return trans.get("translate_result", "翻译错误")
    except Exception as e:
        logger.error(f"翻译过程中发生错误: {e}")
        return "翻译错误"


if __name__ == "__main__":
    # python ai_part/utils/tools.py
    # parse_got_list_api(os.getenv("podcast_site_url"))
    client = OpenAI(api_key=os.getenv("API_KEY"), base_url=os.getenv("BASE_URL"))
    xx = trans_sentense("拐卖中国演员王星的团伙全员被捕", client, "英文")
    logger.info(colored(f"{xx}", "green"))
