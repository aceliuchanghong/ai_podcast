def parse_json2xyz(json_data):
    """
    Convert a list of JSON objects to a formatted string.

    Args:
    json_data (list of dict): A list of dictionaries, where each dictionary contains keys:
        - "speaker" (str): The speaker's name.
        - "text" (str): The text of the speaker.
        - "time_span" (str): The time span of the speech.

    Returns:
    str: A formatted string where each line contains the time span, speaker, and text.
    """
    result = []
    for item in json_data:
        time_span = item.get("time_span", "").split("-")[0]
        speaker = item.get("speaker", "")
        text = item.get("text", "")
        trans_text = item.get("trans_text", "")
        line = f"{time_span} {speaker}: {text}\n{trans_text}"
        result.append(line)

    return "\n".join(result)


def fill_xyz(daily_tts_list):
    daily_tts = daily_tts_list[0]

    title = daily_tts["title"]
    file_path = daily_tts["file_path"]
    detail = parse_json2xyz(daily_tts["detail"])

    print("Title:", title)
    print("File Path:", file_path)
    print("detail:\n", detail)

    return title, file_path, detail


if __name__ == "__main__":
    json_data = [
        {
            "speaker": "Adam",
            "text": "Hey Bella, have you seen the latest news about Li Yanhong and Pony Ma?",
            "trans_text": "嘿，贝拉，你看到关于李彦宏和马化腾的最新消息了吗？",
            "time_span": "00:00:00-00:00:04",
        },
        {
            "speaker": "Bella",
            "text": "Oh, you mean the article from 36Kr? I just read it. It’s quite interesting. They were both in the same photo after years, although they were just distant backs.",
            "trans_text": "哦，你是说36氪的那篇文章？我刚读过。挺有意思的。他们时隔多年又同框了，虽然只是远远的背影。",
            "time_span": "00:00:04-00:00:14",
        },
        {
            "speaker": "Adam",
            "text": "Yes, and the article mentions that they both attended a significant conference with other tech giants like Ren Zhengfei, Lei Jun, and Wang Xing. It seems like a positive sign for the Chinese tech industry.",
            "trans_text": "是的，文章提到他们俩和其他科技巨头如任正非、雷军、王兴一起参加了一个重要的会议。这对中国的科技行业来说似乎是一个积极的信号。",
            "time_span": "00:00:14-00:00:26",
        },
        {
            "speaker": "Bella",
            "text": "Absolutely. The article also points out that the conference included many young talents like Liang Wenfeng from DeepSeek, which shows the industry's revitalization and growth.",
            "trans_text": "绝对。文章还指出，大会包括了许多像来自深寻科技的梁文峰这样的年轻人才，这显示了行业的振兴和增长。",
            "time_span": "00:00:26-00:00:37",
        },
        {
            "speaker": "Adam",
            "text": "Right. The article emphasizes that this trend is reflected in the rising stock prices of major tech companies. And it seems like the back views in the photo symbolize their forward momentum.",
            "trans_text": "好的。文章强调这种趋势反映在主要科技公司股票价格的上涨上。照片中的背景似乎象征着它们的前进步伐。",
            "time_span": "00:00:37-00:00:48",
        },
        {
            "speaker": "Bella",
            "text": "That’s a great point. The article also mentions that companies are starting to collaborate more, especially through DeepSeek. It seems like a turning point from the isolated 'island ecosystem' to a more connected 'technical community.'",
            "trans_text": "这是一个很好的观点。文章还提到，公司开始更多地合作，尤其是通过DeepSeek。这似乎是从孤立的‘孤岛生态系统’向更加互联的‘技术社区’的转折点。",
            "time_span": "00:00:48-00:01:02",
        },
        {
            "speaker": "Adam",
            "text": "Exactly. The article notes that after the first phase of integrating DeepSeek with cloud platforms, some tech giants are moving to the second phase by integrating DeepSeek into their super apps. Baidu Search is the second to do this after WeChat.",
            "trans_text": "确实如此。文章指出，在将DeepSeek与云平台进行第一阶段整合后，一些科技巨头正进入第二阶段，将DeepSeek整合到他们的超级应用中。百度搜索是继微信之后第二个这样做的人。",
            "time_span": "00:01:02-00:01:16",
        },
        {
            "speaker": "Bella",
            "text": "I see. This move by Baidu is quite significant. The article mentions that Li Yanhong has been very committed to developing his own large language models, but now he’s also integrating DeepSeek, which is causing some controversy.",
            "trans_text": "我明白了。百度的这一举动相当重要。文章提到，李彦宏一直非常致力于开发自己的大型语言模型，但现在他还整合了DeepSeek，这引起了一些争议。",
            "time_span": "00:01:16-00:01:31",
        },
        {
            "speaker": "Adam",
            "text": "Yes, it’s a strategic shift. The article suggests that even a company as committed to self-research as Baidu is now integrating external models, which shows how the Chinese internet is moving towards a more interconnected ecosystem.",
            "trans_text": "是的，这是一个战略性的转变。文章指出，即使是像百度这样致力于自主研发的公司，现在也开始整合外部模型，这表明中国互联网正在朝着更加互联的生态系统发展。",
            "time_span": "00:01:31-00:01:44",
        },
        {
            "speaker": "Bella",
            "text": "That’s true. The article also talks about how DeepSeek’s popularity is changing the landscape. WeChat and Baidu Search integrating DeepSeek is a big step towards this new interconnectedness.",
            "trans_text": "确实如此。文章还提到，DeepSeek 的流行正在改变行业格局。微信和百度搜索集成 DeepSeek 是朝着这一新的互联互通迈出的一大步。",
            "time_span": "00:01:44-00:01:56",
        },
        {
            "speaker": "Adam",
            "text": "Absolutely. The article also mentions that DeepSeek’s rapid rise has put pressure on other companies like Alibaba and ByteDance to consider integrating it into their apps.",
            "trans_text": "当然。文章还提到，DeepSeek 的迅速崛起给阿里巴巴和字节跳动等公司带来了压力，促使它们考虑将 DeepSeek 整合到自己的应用中。",
            "time_span": "00:01:56-00:02:06",
        },
        {
            "speaker": "Bella",
            "text": "Yes, it’s interesting to see how this will play out. The article notes that both companies have their own AI development strategies, which might make them more hesitant to integrate DeepSeek.",
            "trans_text": "是的，看看这将如何发展很有趣。文章指出，这两家公司都有自己的人工智能发展战略，这可能使它们在整合 DeepSeek 时更加犹豫。",
            "time_span": "00:02:06-00:02:17",
        },
        {
            "speaker": "Adam",
            "text": "That’s a good point. The article also highlights how DeepSeek’s popularity is forcing these companies to rethink their strategies and potentially collaborate more.",
            "trans_text": "这是一个很好的观点。文章还强调了DeepSeek的受欢迎程度正在迫使这些公司重新考虑他们的策略，并可能加强合作。",
            "time_span": "00:02:17-00:02:26",
        },
        {
            "speaker": "Bella",
            "text": "It’s a fascinating time for the tech industry. I’m curious to see how this integration and collaboration will evolve in the coming months.",
            "trans_text": "这是科技行业的一个令人着迷的时代。我很想知道这种整合与合作在接下来的几个月里将如何发展。",
            "time_span": "00:02:26-00:02:34",
        },
        {
            "speaker": "Adam",
            "text": "Me too. It’s definitely a shift towards a more unified and innovative ecosystem.",
            "trans_text": "我也是。这确实是一个朝着更统一、更创新的生态系统转变的趋势。",
            "time_span": "00:02:34-00:02:39",
        },
    ]

    # python ai_part/utils/parse_xyz.py
    formatted_string = parse_json2xyz(json_data)
    print(formatted_string)
