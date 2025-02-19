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
        return response.json()
    else:
        raise Exception(f"Failed to generate speech: {response.text}")


if __name__ == "__main__":
    # python client.py
    api_key = os.getenv("podcast_api_key")
    # model = "kokoro-82M"
    model = "podcast"
    input_text = "Today is a wonderful day to build something people love!"
    voice = "bella"

    generate_speech(api_key, model, input_text, voice)
    """
    ```
    [
        {
            "title": "3500 元的新 iPhone SE，可能还不是苹果下周最大的惊喜",
            "detail": [
                {
                    "speaker": "Nicole",
                    "text": "Hey Bella, have you heard about Apple's upcoming product launch next Thursday?",
                    "trans_text": "嘿，贝拉，你听说了吗？苹果公司下周四要发布新产品了。",
                    "time_span": "00:00:00-00:00:04",
                },
                {
                    "speaker": "Bella",
                    "text": "Oh, you mean the one where Tim Cook sent out the invitation letter a week early? I'm really curious about what they're calling the “new family member.”",
                    "trans_text": "哦，你是说那个蒂姆·库克提前一周发出邀请函的？我很好奇他们所说的“新家庭成员”到底是什么。",
                    "time_span": "00:00:04-00:00:12",
                },
                {
                    "speaker": "Nicole",
                    "text": "Exactly! It's generating a lot of buzz. They haven't announced the specific date or location, so it's likely they'll release product videos instead of a live event, similar to what they did with the M4 Mac last November.",
                    "trans_text": "没错！它引起了很大的关注。他们还没有宣布具体的日期或地点，所以他们可能会发布产品视频而不是举办现场活动，就像去年11月发布M4 Mac时那样。",
                    "time_span": "00:00:12-00:00:24",
                },
                {
                    "speaker": "Bella",
                    "text": "That makes sense. What are the main products they're expected to launch?",
                    "trans_text": "这说得通。他们计划推出的主要产品有哪些？",
                    "time_span": "00:00:24-00:00:28",
                },
                {
                    "speaker": "Nicole",
                    "text": "Well, the biggest highlight is probably the new iPhone SE 4. It's been heavily rumored and is expected to be a significant upgrade from the previous model.",
                    "trans_text": "最大的亮点可能是新的 iPhone SE 4。这款手机备受传闻，预计将比前代产品有显著的升级。",
                    "time_span": "00:00:28-00:00:37",
                },
                {
                    "speaker": "Bella",
                    "text": "Oh, that sounds interesting! What are the main changes?",
                    "trans_text": "哦，这听起来很有趣！主要的变化是什么？",
                    "time_span": "00:00:37-00:00:40",
                },
                {
                    "speaker": "Nicole",
                    "text": "The iPhone SE 4 will have a more modern design, similar to the iPhone 14. It will lose the Home button and thick bezels, but will likely still have a notch instead of a pill-shaped cutout. The fingerprint sensor will be replaced with Face ID, and it will have a 6.1-inch OLED screen with a 60Hz refresh rate.",
                    "trans_text": "iPhone SE 4将拥有更现代的设计，类似于iPhone 14。它将去掉Home按钮和宽边框，但可能仍会保留刘海而不是药丸形的开孔。指纹传感器将被Face ID取代，并且它将配备6.1英寸的OLED屏幕，刷新率为60Hz。",
                    "time_span": "00:00:40-00:00:58",
                },
                {
                    "speaker": "Bella",
                    "text": "Wow, that's quite an upgrade. What about the camera?",
                    "trans_text": "哇，这真是个大升级。相机怎么样？",
                    "time_span": "00:00:58-00:01:01",
                },
                {
                    "speaker": "Nicole",
                    "text": "The rear camera is expected to be a single 48-megapixel sensor, up from the 12-megapixel on the previous model. The front camera will also be upgraded to 12-megapixels.",
                    "trans_text": "后置摄像头预计将升级为单个4800万像素传感器，而前代产品为1200万像素。前置摄像头也将升级到1200万像素。",
                    "time_span": "00:01:01-00:01:12",
                },
                {
                    "speaker": "Bella",
                    "text": "Impressive! What about the performance?",
                    "trans_text": "令人印象深刻！性能怎么样？",
                    "time_span": "00:01:12-00:01:14",
                },
                {
                    "speaker": "Nicole",
                    "text": "It's expected to have the A18 chip and 8GB of RAM, aligning it with the latest standard iPhone models. There's also a new customizable \"Action Button\" above the volume keys, though it won't have the camera control module like the iPhone 16.",
                    "trans_text": "预计将搭载A18芯片和8GB的RAM，与最新的标准版iPhone型号保持一致。此外，音量键上方还新增了一个可自定义的“动作按钮”，不过它不会像iPhone 16那样配备相机控制模块。",
                    "time_span": "00:01:14-00:01:28",
                },
                {
                    "speaker": "Bella",
                    "text": "That sounds like a lot of improvements. What about the price?",
                    "trans_text": "听起来有很多改进。价格方面呢？",
                    "time_span": "00:01:28-00:01:31",
                },
                {
                    "speaker": "Nicole",
                    "text": "It's rumored to start at 128GB storage for around $499, which is about 3500 RMB after subsidies in China. It could be a strong competitor in the mid-range market.",
                    "trans_text": "据传这款手机将从128GB存储版本起售，价格约为499美元，在中国补贴后大约为3500元人民币。这可能使它成为中端市场的强劲竞争对手。",
                    "time_span": "00:01:31-00:01:43",
                },
                {
                    "speaker": "Bella",
                    "text": "That's great news for budget-conscious buyers. What other products are they expected to launch?",
                    "trans_text": "这对预算有限的买家来说是个好消息。他们还计划推出哪些其他产品？",
                    "time_span": "00:01:43-00:01:48",
                },
                {
                    "speaker": "Nicole",
                    "text": "They might also release the AirTag 2. It's designed to be more secure, with a more difficult-to-remove speaker to prevent misuse. It's also expected to have a second-generation ultra-wideband chip, which will triple the tracking distance.",
                    "trans_text": "他们还可能发布AirTag 2。这款产品设计得更加安全，配备了更难拆卸的扬声器，以防止滥用。预计它还将搭载第二代超宽带芯片，使追踪距离增加三倍。",
                    "time_span": "00:01:48-00:02:01",
                },
                {
                    "speaker": "Bella",
                    "text": "That's a significant improvement. What about the MacBook Air?",
                    "trans_text": "这是个显著的改进。MacBook Air 呢？",
                    "time_span": "00:02:01-00:02:04",
                },
                {
                    "speaker": "Nicole",
                    "text": "The new MacBook Air will likely feature the M4 chip. The design won't change much, but it will come with a base configuration of a slightly underpowered M4, 16GB RAM, and 256GB storage. You can upgrade to the full-powered M4 with 10-core CPU and GPU.",
                    "trans_text": "新款MacBook Air可能会搭载M4芯片。设计方面不会有太大变化，但其基础配置将包括稍显不足的M4芯片、16GB内存和256GB存储空间。你可以选择升级到配备10核CPU和GPU的全性能M4。",
                    "time_span": "00:02:04-00:02:20",
                },
                {
                    "speaker": "Bella",
                    "text": "And what about the iPads?",
                    "trans_text": "那iPad呢？",
                    "time_span": "00:02:20-00:02:21",
                },
                {
                    "speaker": "Nicole",
                    "text": "They're expected to release new versions of the iPad and iPad Air. The iPad 11 will likely get internal upgrades, possibly with the A16 chip, and the iPad Air 7 might have a 90Hz refresh rate screen and the M4 chip.",
                    "trans_text": "他们预计将发布新款的iPad和iPad Air。iPad 11可能会进行内部升级，可能配备A16芯片，而iPad Air 7则可能配备90Hz刷新率的屏幕和M4芯片。",
                    "time_span": "00:02:21-00:02:35",
                },
                {
                    "speaker": "Bella",
                    "text": "That's a lot of exciting updates! What about the HomePad and Apple TV 4K?",
                    "trans_text": "这是很多令人兴奋的更新！HomePad 和 Apple TV 4K 呢？",
                    "time_span": "00:02:35-00:02:40",
                },
                {
                    "speaker": "Nicole",
                    "text": "The HomePad is a new device that could be a wall-mounted display or an integrated HomePod with a 6-inch screen. It will have a camera and support various HomeKit features. The new Apple TV 4K might get the A18 or A17 Pro chip and improved Wi-Fi and Bluetooth.",
                    "trans_text": "HomePad 是一款新设备，可以是壁挂式显示器，也可以是带有 6 英寸屏幕的集成 HomePod。它将配备摄像头并支持各种 HomeKit 功能。新的 Apple TV 4K 可能会配备 A18 或 A17 Pro 芯片，并改进 Wi-Fi 和蓝牙功能。",
                    "time_span": "00:02:40-00:02:56",
                },
                {
                    "speaker": "Bella",
                    "text": "It sounds like a busy and exciting launch! Which product are you most looking forward to?",
                    "trans_text": "听起来是一次忙碌而令人兴奋的发布会！你最期待哪个产品？",
                    "time_span": "00:02:56-00:03:01",
                },
                {
                    "speaker": "Nicole",
                    "text": "I'm really excited about the iPhone SE 4. It's a great balance of performance and affordability. What about you?",
                    "trans_text": "我非常期待iPhone SE 4。它在性能和价格上取得了很好的平衡。你呢？",
                    "time_span": "00:03:01-00:03:08",
                },
                {
                    "speaker": "Bella",
                    "text": "I'm definitely interested in the HomePad. It could be a game-changer for smart home integration.",
                    "trans_text": "我对HomePad非常感兴趣。它可能会成为智能家居集成的改变者。",
                    "time_span": "00:03:08-00:03:14",
                },
            ],
            "file_path": "/root/mnt/data/llch/ai_podcast/no_git_oic/73bfd15c9dda723aa214491ba22e87ed.wav",
        }
    ]
    ```
    """
