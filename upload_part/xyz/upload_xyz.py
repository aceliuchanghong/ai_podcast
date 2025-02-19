import os
from dotenv import load_dotenv
import logging
from termcolor import colored
import sys
from playwright.async_api import async_playwright
import asyncio

load_dotenv()
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s-%(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

from upload_part.uploader import Upload


class XyzUploader(Upload):
    def __init__(self):
        self.platform = "xyz"

    async def upload(
        self,
        title: str,
        wav_file_path: str,
        detail: str,
        headless: bool = False,
    ):
        try:
            logger.info(colored(f"1. Start to upload:{title}", "green"))
            async with async_playwright() as playwright:
                chromium = playwright.chromium
                browser = await chromium.launch(headless=headless)
                page = browser.new_page()
                page.goto("http://example.com")
                browser.close()
        except Exception as e:
            logger.error(colored(f"Failed to upload to XYZ: {e}", "red"))
            sys.exit(1)


if __name__ == "__main__":
    # python upload_part/xyz/upload_xyz.py
    xyz = XyzUploader()
    asyncio.run(xyz.upload("test", "test.wav", "test"))
