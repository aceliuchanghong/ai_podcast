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
    pattern = re.compile(r"(\d+\.\s+)?(Adam|Bella):\s*(.*)")

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
            logger.info(colored(f"已生成的:{alredy_post_list}", "green"))
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


def download_cover(cover_url: str, cover_path: str) -> None:
    if cover_url == "":
        return
    try:
        response = requests.get(cover_url)
        if response.status_code == 200:
            with open(cover_path, "wb") as f:
                f.write(response.content)
        else:
            logger.error(f"下载封面图失败：{response.status_code}, URL: {cover_url}")
    except requests.exceptions.RequestException as e:
        logger.error(f"下载封面图异常: {e}, URL: {cover_url}")


def parse_got_list_api_bak(url: str, nums: int = 1) -> list:
    hot_list_platform = [
        "36kr",
        "ithome",
        "thepaper",
        "weread",
        "douban-group",
        "hellogithub",
        "zhihu-daily",
    ]
    result = []
    platform = hot_list_platform[0]

    def fetch_data(url, platform):
        try:
            response = requests.get(url + platform)
            if response.status_code == 200:
                return response.json()["data"]
            else:
                logger.error(f"请求失败，状态码：{response.status_code}, URL: {url}")
                print(f"请求失败，状态码：{response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常: {e}, URL: {url}")
            print(f"请求异常: {e}")
            return None

    # Get already generated URLs
    alredy_gen_url_list = execute_sqlite_sql(select_all_url_sql)
    # print(f"已生成的:{alredy_gen_url_list}")
    if len(alredy_gen_url_list) == 0 or alredy_gen_url_list[0][0] is None:
        alredy_gen_url_list = []
    alredy_gen_url_list = [item[0] for item in alredy_gen_url_list]
    # logger.info(colored(f"已生成的:{alredy_gen_url_list}", "green"))

    for platform in hot_list_platform:
        if len(result) >= nums:
            break

        logger.info(colored(f"尝试从平台 {platform} 获取文章", "yellow"))
        data = fetch_data(url, platform)
        if data is None:
            continue

        for index in range(len(data)):
            cover_url = data[index].get("cover", "")
            if cover_url != "":
                save_cover_path = os.getenv("pic_save_path")
                save_cover_name = (
                    f"{platform}_{compute_mdhash_id(data[index].get("title", ""))}.jpg"
                )
                os.makedirs(save_cover_path, exist_ok=True)
                cover_path = os.path.join(save_cover_path, save_cover_name)
            else:
                cover_path = os.getenv("default_cover_path")
            download_cover(cover_url, cover_path)

            temp_item = {
                "title": data[index].get("title", ""),
                "cover": cover_path,
                "url": data[index].get("url", ""),
            }
            if temp_item["url"] not in alredy_gen_url_list and temp_item["url"] not in [
                item["url"] for item in result
            ]:
                result.append(temp_item)

            if len(result) >= nums:
                break

    if len(result) > nums:
        result = result[:nums]

    return result if result else []


def trans_sentense(sentense: str, client: OpenAI, language: str = "English") -> str:
    if language not in ["Chinese", "English"]:
        raise ValueError("只支持Chinese和English翻译")
    prompt = f"Please translate the following content into idiomatic {language} and return it in JSON format:\n{sentense}\nexample:\n{{'translate_result': 'translated content'}}"
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
    system_prompt: Optional[str] = "You are a professional secretary.",
    language: str = "English",
    max_retries: int = 3,
) -> str:
    if language not in ["中文", "English"]:
        raise ValueError("只支持中文和English剧本")
    prompt = (
        f"Convert the news content provided by the leader into a pure {language} script of a dialogue between Adam and Bella, without any Chinese characters:\narticle_content:\n```"
        + article_content
        + "```\n"
        + "1. Do not output any text other than the script content\n"
        + "2. The script content must be valuable and substantial\n"
        + "3. Output-example:\n"
        + "```\n"
        + "1. Adam: Hey Bella, have you heard about Apple's upcoming product launch next Thursday?\n"
        + "2. Bella: Oh, you mean the one where Tim Cook sent out the invitation letter a week early? I'm really curious about what they're calling the “new family member.”\n"
        + "3. Adam: Exactly! It's generating a lot of buzz. They haven't announced the specific date or location, so it's likely they'll release product videos instead of a live event, similar to what they did with the M4 Mac last November.\n"
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
        ("Adam", "I don't really feel like talking this time."),
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

    # article_list = parse_got_list_api(os.getenv("podcast_site_url"), 1)
    # logger.info(colored(f"文章列表:{article_list}", "green"))

    article_list = parse_got_list_api_bak(os.getenv("bak_podcast_site_url"), 1)
    logger.info(
        colored(f"\n文章列表:{article_list}\n文章数量:{len(article_list)}", "green")
    )
