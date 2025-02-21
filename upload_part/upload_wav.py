import os
from dotenv import load_dotenv
import logging
from termcolor import colored
import sys
import json

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
    os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../")),
)

from upload_part.xyz.upload_xyz import upload_wav
from client import generate_speech
from refresh_token import xyz_main

if __name__ == "__main__":
    """
    python upload_part/upload_wav.py
    nohup python upload_part/upload_wav.py > no_git_oic/upload_wav.log 2>&1 &
    """
    api_key = os.getenv("podcast_api_key")
    model = "podcast"
    token_file = "no_git_oic/xyz_token.json"

    for i in range(20):
        gen_wav_detail_list = generate_speech(api_key, model)
        xyz_main()
        with open(token_file, "r") as f:
            tokens = json.load(f)
            access_token = tokens.get("accessToken")
        upload_wav(access_token, gen_wav_detail_list[0]["file_path"])
        logger.info(colored(f"upload_wav {i} done", "green"))
