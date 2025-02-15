import os
from dotenv import load_dotenv
import logging
from termcolor import colored
import litserve as ls
from openai import OpenAI

load_dotenv()
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s-%(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class PodcastServer(ls.LitAPI):
    def setup(self, device):
        self.server_name = "PodcastServer"
        self.client = OpenAI(
            api_key=os.getenv("API_KEY"), base_url=os.getenv("BASE_URL")
        )

    def decode_request(self, request):
        return request["input"]

    def predict(self, inputs):
        output = inputs
        return output

    def encode_response(self, output):
        return {"output": output}


if __name__ == "__main__":
    """
    python podcast_server.py
    nohup python podcast_server.py > no_git_oic/podcast_server.log 2>&1 &
    """
    api = PodcastServer()
    server = ls.LitServer(api)
    server.run(port=int(os.getenv("podcast_port", 21500)))
