
# 특별 이벤트 소문 설정
special_events = [
    {
        "npc": "이레인 바일",
        "date": "2025-04-30",
        "weather": "천둥",
        "message": "…그림자 속에서 누군가의 이름이 들려왔어요. 그건 라일리였어요. 분명히요."
    },
    {
        "npc": "카스파 라비에",
        "date": "2025-05-01",
        "message": "나는 봤어. 지하실 문이 열리는 순간을. 그가 돌아올 거야."
    }
]

# 이벤트 소문 감지 함수
def get_event_rumor(npc_name, today_str, weather):
    for event in special_events:
        if event["npc"] == npc_name and event["date"] == today_str:
            if "weather" in event:
                if event["weather"] == weather:
                    return event["message"]
            else:
                return event["message"]
    return None


def log_player_input(npc_name, player, raw_text):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv("GOOGLE_CREDENTIALS_JSON"), scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID")).worksheet("player_input")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([timestamp, npc_name, player, raw_text])


import gspread
from oauth2client.service_account import ServiceAccountCredentials

def log_rumor(npc_name, player, text):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv("GOOGLE_CREDENTIALS_JSON"), scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID")).worksheet("log")
    sheet.append_row([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), npc_name, player, text])


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

    
    # 기억 상태에 따른 시점별 프롬프트 추가 설명
    memory_description = ""
    if npc["기억 상태"] == "명확":
        memory_description = "그는 마치 어제 일어난 일처럼 또렷이 기억합니다."
    elif npc["기억 상태"] == "흐릿":
        memory_description = "기억은 희미하고, 마치 꿈에서 본 것처럼 정확하지 않습니다."
    elif npc["기억 상태"] == "왜곡":
        memory_description = "그의 기억은 뒤틀려 있으며, 실제와는 다르게 믿고 있습니다."
    elif npc["기억 상태"] == "없음":
        memory_description = "그는 그 이름조차 들은 적 없다고 말합니다. 하지만 감정 어딘가에 흔적이 남은 듯합니다."

    base_prompt = f"""
설정된 기억 상태에 따른 설명: {{memory_description}}
""" + f"""

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
                    event_rumor = get_event_rumor(npc_name, datetime.datetime.now().strftime("%Y-%m-%d"), weather)
                    if event_rumor:
                        rumor = event_rumor
                    else:
                        rumor = generate_rumor(prompt)
                    npc_name = npc["이름"]
tone = npc["말투 특징"]
gesture = npc["행동 특징"]
combined_stage = f"{gesture}, {tone}"
stylized = f"{npc_name} ({combined_stage}) \"{rumor}\""
log_player_input(npc_name, acct, content)
mastodon.status_post(f"@{acct} {stylized}", in_reply_to_id=status_id, visibility="unlisted")
                    log_rumor(npc_name, acct, rumor)
                else:
                    mastodon.status_post(f"@{acct} 그런 이름의 학생은 없는 것 같아…", in_reply_to_id=status_id, visibility="unlisted")

if __name__ == "__main__":
    print("🌀 NPC 루머봇 실행 중...")
    mastodon.stream_user(RumorListener())
