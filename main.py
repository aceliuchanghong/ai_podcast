import os
from dotenv import load_dotenv
import logging
from termcolor import colored
import re
import json

load_dotenv()
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s-%(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

from upload_part.xyz.login.cookie_getter import (
    send_login_request,
    complete_login_with_verify_code,
    get_url_response,
)


def check_token_expiration(access_token, check_url):
    response = get_url_response(check_url, access_token)
    return response.status_code == 200


def xyz_main():
    phone_number = os.getenv("MOBILE_NUMBER")
    send_login_request_url = os.getenv("xyz_send_code_url")
    complete_login_url = os.getenv("xyz_complete_login_url")
    check_url = os.getenv("xyz_check_url")
    need_login = True

    if not phone_number:
        logger.error(colored("Phone number not provided in environment.", "red"))
        return

    token_file = "no_git_oic/xyz_token.json"
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            try:
                tokens = json.load(f)
                access_token = tokens.get("accessToken")
                refresh_token = tokens.get("refreshToken")
                if check_token_expiration(access_token, check_url):
                    need_login = False
            except json.JSONDecodeError:
                logger.warning(
                    colored(
                        "0.Failed to read token file, proceeding with login.", "yellow"
                    )
                )
    if need_login:
        while True:
            still_login = input(
                colored("Cookie过期,仍需要登录吗? yes/no: ", "yellow")
            ).lower()
            if still_login == "yes":
                break
            elif still_login == "no":
                return
            else:
                logger.warning(colored("Only yes/no, please re-enter.", "yellow"))
        logger.info(colored(f"\n\n\n1. {phone_number} starting login", "green"))

        login_request = send_login_request(phone_number, send_login_request_url)
        if login_request:
            logger.info(colored(f"2. Verification code request sent...", "green"))
        else:
            logger.error(colored(f"Verification code request failed", "red"))
            return

        while True:
            verification_code = input(
                colored("Please enter the 4-digit verification code: ", "yellow")
            )
            if re.match(r"^\d{4}$", verification_code):
                break
            else:
                logger.warning(
                    colored(
                        "Invalid verification code format, please re-enter.", "yellow"
                    )
                )

        access_token, refresh_token = complete_login_with_verify_code(
            phone_number, complete_login_url, verification_code
        )
        if access_token and refresh_token:
            logger.info(
                colored(
                    f"3. Token acquisition suc:\naccessToken:{access_token}",
                    "green",
                )
            )
            with open(token_file, "w") as f:
                json.dump(
                    {"accessToken": access_token, "refreshToken": refresh_token}, f
                )
        else:
            logger.error(colored("Failed to acquire token", "red"))
            return

    # Check token expiration after saving
    if check_token_expiration(access_token, check_url):
        logger.info(colored(f"4. GO!GO!GO!", "green"))
    else:
        logger.error(colored(f"4. Token has expired", "red"))


if __name__ == "__main__":
    """
    python main.py
    """
    xyz_main()
