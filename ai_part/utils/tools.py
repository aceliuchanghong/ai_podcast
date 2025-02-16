import os
from dotenv import load_dotenv
import logging
from termcolor import colored
import requests
from openai import OpenAI
import sys
from typing import Optional
import time
import re

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
from ai_part.crawler.crawler_by_jina import jina_request
from ai_part.utils.sql_sentence import *
from ai_part.utils.check_db import execute_sqlite_sql
from ai_part.tts.kokoro_by_deepinfra import compute_mdhash_id


def parse_dialogue(dialogue_str):
    # 定义正则表达式模式
    pattern = re.compile(r"(\d+\.\s+)?(Nicole|Bella):\s*(.*)")

    # 初始化结果列表
    dialogue_list = []

    # 按行分割对话内容
    lines = dialogue_str.strip().split("\n")

    # 遍历每一行，匹配正则表达式
    for line in lines:
        match = pattern.match(line)
        if match:
            # 提取说话者和对话内容
            speaker = match.group(2)
            content = match.group(3).strip()
            dialogue_list.append((speaker, content))

    return dialogue_list


def parse_got_list_api(url: str, nums: int = 2) -> list:
    """
    [{'title': '苹果下周最大的惊喜', 'hot': '538.00热度', 'url': 'https://36kr.com/p/3167297655974408', 'mobil_url': 'https://m.36kr.com/p/3167297655974408', 'index': 1},...]
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # logger.info(colored(f"成功获取数据: {data['data'][:nums]}", "green"))
            alredy_post_list = execute_sqlite_sql(select_all_url_sql)
            alredy_post_list = [item[0] for item in alredy_post_list]
            logger.info(colored(f"{alredy_post_list}", "green"))
            filtered_data = [
                item for item in data["data"] if item["url"] not in alredy_post_list
            ]

            result_data_list = filtered_data[:nums]
            for item in result_data_list:
                code = compute_mdhash_id(item["title"])
                execute_sqlite_sql(
                    insert_basic_info_sql,
                    (item["title"], item["url"], code, ""),
                )
            return result_data_list
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
    prompt = f"请将以下内容翻译成地道的{language},以json格式返回:\n{sentense}\nexample:\n{{'translate_result': '翻译后的内容'}}"
    try:
        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "qwen2.5:7b-instruct-fp16"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        only_str = response.choices[0].message.content
        # logger.info(colored(f"llm-output:{only_str}", "green"))
        trans = parse_and_check_json_markdown(only_str, ["translate_result"])
        return trans.get("translate_result", f"翻译错误{only_str}")
    except Exception as e:
        logger.info(colored(f"翻译过程中发生错误: {e}\n{only_str}", "red"))
        return "翻译错误"


def get_sentense_list(
    article_content: str,
    client: OpenAI,
    model: Optional[str] = os.getenv("LLM_MODEL"),
    system_prompt: Optional[str] = "你是一个专业的秘书",
    language: str = "英文",
    max_retries: int = 3,
) -> str:
    if language not in ["中文", "英文"]:
        raise ValueError("只支持中文和英文剧本")
    prompt = (
        f"将领导提供的新闻内容转化为 Nicole 与 Bella 对话的{language}剧本:\narticle_content:\n```"
        + article_content
        + "```\n"
        + "1.不要有除了剧本内容以外的文字输出\n"
        + "2.剧本内容有价值,需要言之有物\n"
        + "3.output-example:\n"
        + "```\n"
        + "1. Nicole: Hey Bella, have you heard about Apple's upcoming product launch next Thursday?\n"
        + "2. Bella: Oh, you mean the one where Tim Cook sent out the invitation letter a week early? I'm really curious about what they're calling the “new family member.”\n"
        + "3. Nicole: Exactly! It's generating a lot of buzz. They haven't announced the specific date or location, so it's likely they'll release product videos instead of a live event, similar to what they did with the M4 Mac last November.\n"
        + "4. Bella: That makes sense. What are the main products they're expected to launch?\n"
        + "```\n"
    )
    messages = [{"role": "user", "content": prompt}]

    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})

    start_time = time.time()
    for attempt in range(max_retries):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=8192,
        )

        result = parse_dialogue(response.choices[0].message.content)
        if result is not None:
            return result
        logger.warning(f"尝试 {attempt + 1} 次解析对话失败，将重试...")

    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(colored(f"获取剧本耗时: {elapsed_time:.2f}秒", "green"))

    logger.error("达到最大重试次数，解析对话失败")
    return [
        ("Nicole", "I don't really feel like talking this time."),
        ("Bella", "Oh, fine, maybe next time."),
    ]


if __name__ == "__main__":
    # python ai_part/utils/tools.py

    # client = OpenAI(api_key=os.getenv("API_KEY"), base_url=os.getenv("BASE_URL"))

    # article_list = parse_got_list_api(os.getenv("podcast_site_url"), 1)
    # logger.info(colored(f"文章列表:{article_list}", "green"))

    # for article in article_list:
    #     article_info = {}
    #     # 获取文章标题
    #     article_info["title"] = article["title"]
    #     article_info["detail"] = []
    #     article_info["file_path"] = "init"
    #     # 获取文章内容
    #     today_article_content = jina_request(
    #         url=article["url"],
    #         authorization_token=os.getenv("JINA_API_KEY"),
    #     )
    #     # logger.info(colored(f"文章内容:{today_article_content}", "green"))
    #     result = get_sentense_list(today_article_content, client)
    #     logger.info(colored(f"剧本内容:{result}", "green"))

    # xx = trans_sentense("拐卖中国演员王星的团伙全员被捕", client, "英文")
    # logger.info(colored(f"{xx}", "green"))

    article_list = parse_got_list_api(os.getenv("podcast_site_url"), 1)
    logger.info(colored(f"文章列表:{article_list}", "green"))
