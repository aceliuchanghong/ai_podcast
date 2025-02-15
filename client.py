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


def generate_speech(api_key, model, input_text, voice):
    url = "http://127.0.0.1:21500/v1/audio/speech"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": model, "input": input_text, "voice": voice}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        logger.info(colored(f"{response.text}", "green"))
    else:
        print(f"Error: {response.status_code} - {response.text}")


if __name__ == "__main__":
    # python client.py
    api_key = os.getenv("podcast_api_key")
    # model = "kokoro-82M"
    model = "podcast"
    input_text = "Today is a wonderful day to build something people love!"
    voice = "bella"

    generate_speech(api_key, model, input_text, voice)
