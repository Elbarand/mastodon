import os
import re
import random
import datetime
import pandas as pd
from mastodon import Mastodon, StreamListener
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Load NPC data
npc_df = pd.read_csv("npc_data_full.csv")

# GPT 설정
openai_client = OpenAI()
openai_api_key = os.getenv("OPENAI_API_KEY")

# 마스토돈 설정
mastodon = Mastodon(
    access_token=os.getenv("MASTODON_ACCESS_TOKEN"),
    api_base_url=os.getenv("MASTODON_BASE_URL")
)

# 현재 날씨를 간단히 무작위로 설정 (임시)
def get_current_weather():
    return random.choice(["맑음", "비", "흐림", "안개", "천둥", "바람", "눈", "습기"])

# GPT 프롬프트 생성
def create_prompt(npc, weather):
    memory = npc["기억 내용"]
    style = npc["소문 스타일"]
    tone = npc["말투 특징"]
    mood = npc["감정"]

    base_prompt = f"""
NPC는 플레이어와 직접 대화하지 않으며, 마치 주변에 흘리는 듯한 '소문'을 퍼뜨리는 역할입니다.
NPC의 이름은 {npc["이름"]}이며, {npc["기숙사"]} 기숙사 소속입니다.
현재 날씨는 {weather}입니다. 이 NPC는 '{npc["좋아하는 날씨"]}'를 좋아하고, '{npc["싫어하는 날씨"]}'를 싫어합니다.

기억 상태는 '{npc["기억 상태"]}'이고, 이렇게 기억합니다: "{memory}"
이 NPC는 말투가 "{tone}"이고, 감정 상태는 "{mood}"입니다.
소문 전파 방식은 "{style}"입니다.

다음 조건을 바탕으로 1~2문장으로 된 가볍고 불완전한 소문을 흘려주세요. (직접적인 단정은 피하고 모호하게!)
- 플레이어와 직접 대화하지 않기
- 라일리라는 인물의 존재 여부는 혼란스럽게 표현
- 날씨가 감정과 말투에 영향을 미칠 수 있음
"""

    return base_prompt.strip()

# GPT 요청
def generate_rumor(prompt):
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                { "role": "system", "content": "당신은 마법학교의 NPC입니다. 플레이어와 대화하지 않고 혼잣말처럼 소문을 흘립니다." },
                { "role": "user", "content": prompt }
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "…아무 말도 흘리지 않았다."

# 멘션 감지
class RumorListener(StreamListener):
    def on_notification(self, notification):
        if notification["type"] == "mention":
            content = notification["status"]["content"]
            acct = notification["account"]["acct"]
            status_id = notification["status"]["id"]

            match = re.search(r"\[(.+?)/소문\]", content)
            if match:
                npc_name = match.group(1).strip()
                result = npc_df[npc_df["이름"] == npc_name]

                if not result.empty:
                    npc = result.iloc[0]
                    weather = get_current_weather()
                    prompt = create_prompt(npc, weather)
                    rumor = generate_rumor(prompt)
                    mastodon.status_post(f"@{acct} {rumor}", in_reply_to_id=status_id, visibility="unlisted")
                else:
                    mastodon.status_post(f"@{acct} 그런 이름의 학생은 없는 것 같아…", in_reply_to_id=status_id, visibility="unlisted")

if __name__ == "__main__":
    print("🌀 NPC 루머봇 실행 중...")
    mastodon.stream_user(RumorListener())
