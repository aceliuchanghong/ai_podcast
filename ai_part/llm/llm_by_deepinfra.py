import os
from dotenv import load_dotenv
import logging
from termcolor import colored
from openai import OpenAI
from typing import Optional

load_dotenv()
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s-%(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def get_llm_answer(
    question: str,
    client: OpenAI,
    model: Optional[str] = "Qwen/Qwen2.5-72B-Instruct",
    system_prompt: Optional[str] = None,
) -> str:
    """
    使用OpenAI的Chat API获取问题的答案。

    :param question: 用户提出的问题。
    :param client: OpenAI客户端对象。
    :param system_prompt: 可选的系统提示，用于指导模型的行为。
    :return: 模型生成的答案。
    """
    messages = [{"role": "user", "content": question}]

    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=8192,
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    """
    python ai_part/llm/llm_by_deepinfra.py
    """
    prompt = "What is the capital of France?"
    client = OpenAI(api_key=os.getenv("API_KEY"), base_url=os.getenv("BASE_URL"))
    xx = get_llm_answer(prompt, client)
    logger.info(colored(f"{xx}", "green"))
