import os
import random
import datetime
from mastodon import Mastodon
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 마스토돈 설정
mastodon = Mastodon(
    access_token=os.getenv("MASTODON_ACCESS_TOKEN"),
    api_base_url=os.getenv("MASTODON_BASE_URL")
)

# GPT 설정
openai_client = OpenAI()
openai_api_key = os.getenv("OPENAI_API_KEY")

# 가능한 날씨
weather_types = ["맑음", "흐림", "비", "눈", "바람", "천둥", "안개", "습기"]

def get_random_weather():
    return random.choice(weather_types)

def make_weather_notice(weather):
    today = datetime.datetime.now().strftime("%Y년 %m월 %d일 (%a)")
    prompt = f"""
오늘은 마법학교 전체 게시판에 붙는 날씨 대자보를 작성하는 날입니다.
날씨는 '{weather}'입니다. 마법학교답게 약간의 비유나 암시가 섞인 표현으로 날씨를 소개하고,
어떤 NPC나 기숙사가 날씨에 영향을 받을지도 가볍게 암시해주세요.

형식:
📌 오늘의 마법학교 날씨
━━━━━━━━━━━━━━━
<예쁜 한 문단>
━━━━━━━━━━━━━━━

말투는 정중하면서도 고풍스럽고 시적인 감성이 담긴 공지 형식으로 작성해 주세요.
"""
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                { "role": "system", "content": "당신은 마법학교에서 날씨 대자보를 작성하는 교무실 보조 요정입니다." },
                { "role": "user", "content": prompt }
            ]
        )
        notice_text = response.choices[0].message.content.strip()
        return f"{today}\n{notice_text}"
    except Exception as e:
        return f"{today}\n📌 오늘의 마법학교 날씨\n━━━━━━━━━━━━━━━\n{weather}입니다. 특별한 일이 일어날지도 몰라요.\n━━━━━━━━━━━━━━━"

if __name__ == "__main__":
    weather = get_random_weather()
    notice = make_weather_notice(weather)
    print("📮 대자보 발송 중...")
    mastodon.toot(notice)
