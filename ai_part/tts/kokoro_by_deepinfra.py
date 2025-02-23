import requests
import json
import os
from dotenv import load_dotenv
import logging
from termcolor import colored
import base64
from hashlib import md5
from typing import Union

load_dotenv()
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s-%(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

CHOICES = [
    "af_bella",  # 0
    "af_alloy",
    "af_aoede",
    "af_heart",
    "af_jessica",
    "af_kore",
    "af_nicole",  # 6
    "af_nova",
    "af_river",
    "af_sarah",
    "af_sky",
    "am_adam",  # 11
    "am_echo",  # 12
    "am_eric",
    "am_fenrir",
    "am_liam",
    "am_michael",
    "am_onyx",
    "am_puck",
    "am_santa",
    "bf_alice",
    "bf_emma",
    "bf_isabella",
    "bf_lily",
    "bm_daniel",
    "bm_fable",
    "bm_george",
    "bm_lewis",
    "ef_dora",
    "em_alex",
    "em_santa",
    "ff_siwis",
    "hf_alpha",
    "hf_beta",
    "hm_omega",
    "hm_psi",
    "if_sara",
    "im_nicola",
    "jf_alpha",
    "jf_gongitsune",
    "jf_nezumi",
    "jf_tebukuro",
    "jm_kumo",
    "pf_dora",
    "pm_alex",
    "pm_santa",
    "zf_xiaobei",
    "zf_xiaoni",
    "zf_xiaoxiao",
    "zf_xiaoyi",
    "zm_yunjian",
    "zm_yunxi",
    "zm_yunxia",
    "zm_yunyang",
]


def compute_mdhash_id(content, prefix: str = ""):
    return prefix + md5(content.encode()).hexdigest()


def save_base64_wav(base64_string, output_file_path):
    """
    将 base64 编码的 WAV 数据解码并保存为 WAV 文件。

    :param base64_string: 包含 base64 编码的 WAV 数据的字符串
    :param output_file_path: 保存 WAV 文件的路径
    """
    # 去掉 data:audio/wav;base64, 前缀
    if base64_string.startswith("data:audio/wav;base64,"):
        base64_string = base64_string[len("data:audio/wav;base64,") :]

    wav_data = base64.b64decode(base64_string)

    with open(output_file_path, "wb") as wav_file:
        wav_file.write(wav_data)

    # print(f"WAV 文件已保存到: {output_file_path}")


def send_text_to_speech(
    text: str,
    preset_voice_num: Union[str, int] = 0,
    output_file_destination: str = "no_git_oic",
    file_name: str = "output.wav",
) -> str:
    """
    将文本转换为语音并保存为 WAV 文件。

    :param text: 要转换的文本
    :param output_file_destination: 输出文件路径，默认为 "no_git_oic"
    :param preset_voice_num: 预设的语音列表，默认为 ["af_bella"]
    :return: 输出文件路径
    :raises: Exception 如果请求失败
    """
    if isinstance(preset_voice_num, str):
        try:
            preset_voice_num = CHOICES.index(preset_voice_num)
        except ValueError:
            preset_voice_num = 0
    if preset_voice_num < 0 or preset_voice_num >= len(CHOICES):
        raise ValueError(
            f"Invalid preset_voice_num. Must be between 0 and {len(CHOICES)}."
        )
    preset_voice = [CHOICES[preset_voice_num]]
    os.makedirs(output_file_destination, exist_ok=True)

    output_file = os.path.join(
        output_file_destination,
        compute_mdhash_id(text + str(preset_voice_num)) + ".wav",
    )
    if os.path.exists(output_file):
        print(f"{output_file} already exists.")
        return output_file

    headers = {
        "Authorization": "bearer " + os.getenv("API_KEY"),
        "Content-Type": "application/json",
    }
    data = {
        "text": text,
        "output_format": "wav",
        "preset_voice": preset_voice,
        "speed": 1.0,
        "stream": False,
    }
    response = requests.post(
        os.getenv("KOKORO_URL"), headers=headers, data=json.dumps(data)
    )

    # logger.info(
    #     colored(
    #         f"\n"
    #         f"request_id: {response.json()['request_id']}\n"
    #         f"inference_status: {response.json()['inference_status']}\n"
    #         f"input_character_length: {response.json()['input_character_length']}\n"
    #         f"output_format: {response.json()['output_format']}",
    #         "green",
    #     )
    # )

    # 保存音频文件
    if file_name != "output.wav":
        output_file = file_name
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
    save_base64_wav(response.json().get("audio"), output_file)

    if response.status_code == 200:
        return output_file
    else:
        raise Exception(
            f"Request failed with status code {response.status_code}: {response.text}"
        )


if __name__ == "__main__":
    """
    python ai_part/tts/kokoro_by_deepinfra.py
    """
    text = "How could you know? It's an unanswerable question. Like asking an unborn child if they'll lead a good life. They haven't even been born."
    preset_voice_num = 0

    audio_content = send_text_to_speech(text, preset_voice_num)
