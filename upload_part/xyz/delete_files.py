import os
from dotenv import load_dotenv
import logging
from termcolor import colored
import requests
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

from refresh_token import refersh_xyz


def delete_wav_files():
    access_token = refersh_xyz()
    payload = {
        "pid": os.getenv("bella_pid"),
        "limit": 1000,
        "skip": 0,
        "type": "AUDIO",
    }
    xyz_list_url = os.getenv("xyz_list_url")
    xyz_rm_url = os.getenv("xyz_delete_url")
    headers = {"x-jike-access-token": access_token, "x-pid": os.getenv("bella_pid")}

    response = requests.post(xyz_list_url, headers=headers, json=payload)
    files_list = []
    # fmt: off
    if response.status_code == 200:
        try:
            files = response.json()
            files_list = [file_info["id"] for file_info in files["data"]]
            logger.info(colored(f"音频待删除数量:{len(files_list)}", "green"))
            
            for file_id in files_list:
                del_payload = {"resourceId": file_id}
                del_response = requests.post(xyz_rm_url, headers=headers, json=del_payload)
                
                if del_response.status_code == 200:
                    logger.info(colored(f"del_wav_suc:{file_id}", "green"))
                else:
                    logger.warning(colored(f"Failed to delete file {file_id}. Status code: {del_response.status_code}", "red"))
                    logger.error(colored(f"Response content: {del_response.text}", "red"))
        except ValueError as ve:
            logger.error(colored(f"Error parsing JSON response: {ve}", "red"))
        except KeyError as ke:
            logger.error(colored(f"Key error in JSON response: {ke}", "red"))
        except Exception as e:
            logger.error(colored(f"Unexpected error occurred: {e}", "red"))
    else:
        logger.error(colored(f"DEL Error: {response.status_code}", "red"))
    # fmt: on


def delete_pic_files():
    access_token = refersh_xyz()
    payload = {
        "pid": os.getenv("bella_pid"),
        "limit": 1000,
        "skip": 0,
        "type": "IMAGE",
    }
    xyz_list_url = os.getenv("xyz_list_url")
    xyz_rm_url = os.getenv("xyz_delete_url")
    headers = {"x-jike-access-token": access_token, "x-pid": os.getenv("bella_pid")}

    response = requests.post(xyz_list_url, headers=headers, json=payload)
    files_list = []
    # fmt: off
    if response.status_code == 200:
        try:
            files = response.json()
            files_list = [file_info["id"] for file_info in files["data"]]
            logger.info(colored(f"图片待删除数量:{len(files_list)}", "green"))
            
            for file_id in files_list:
                del_payload = {"resourceId": file_id}
                del_response = requests.post(xyz_rm_url, headers=headers, json=del_payload)
                
                if del_response.status_code == 200:
                    logger.info(colored(f"del_pic_suc:{file_id}", "green"))
                else:
                    logger.warning(colored(f"Failed to delete file {file_id}. Status code: {del_response.status_code}", "red"))
                    logger.error(colored(f"Response content: {del_response.text}", "red"))
        except ValueError as ve:
            logger.error(colored(f"Error parsing JSON response: {ve}", "red"))
        except KeyError as ke:
            logger.error(colored(f"Key error in JSON response: {ke}", "red"))
        except Exception as e:
            logger.error(colored(f"Unexpected error occurred: {e}", "red"))
    else:
        logger.error(colored(f"DEL Error: {response.status_code}", "red"))
    # fmt: on


if __name__ == "__main__":
    # python upload_part/xyz/delete_files.py
    delete_wav_files()
    delete_pic_files()
