import os
import time
import datetime
from mastodon import StreamListener
from mastodon_config import mastodon
from personality import respond
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

# 시트 연결
def connect_to_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv("GOOGLE_CREDENTIALS_JSON"), scope)
    client = gspread.authorize(creds)
    return client.open_by_key(os.getenv("GOOGLE_SHEET_ID"))

# 출석 처리
def handle_attendance(sheet, user_id):
    player_tab = sheet.worksheet("플레이어")
    records = player_tab.get_all_records()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    now_hour = datetime.datetime.now().hour

    for i, row in enumerate(records):
        if row["ID"] == user_id:
            if row["출석일"] == today:
                return respond("출석중복")
            if now_hour >= 22:
                return respond("출석22시후")
            player_tab.update_cell(i+2, 4, today)
            player_tab.update_cell(i+2, 3, row["갈레온"] + 2)
            return respond("출석")
    return respond("등록안됨")

# 과제 처리
def handle_homework(sheet, user_id):
    player_tab = sheet.worksheet("플레이어")
    records = player_tab.get_all_records()

    for i, row in enumerate(records):
        if row["ID"] == user_id:
            if row["과제"] >= 4:
                return respond("과제초과")
            player_tab.update_cell(i+2, 5, row["과제"] + 1)
            player_tab.update_cell(i+2, 3, row["갈레온"] + 5)
            return respond("과제")
    return respond("등록안됨")

# 자동 멘트
def send_scheduled_message(sheet):
    now = datetime.datetime.now().strftime("%H:%M")
    prof_tab = sheet.worksheet("professor")
    rows = prof_tab.get_all_records()
    for row in rows:
        if row["시간"] == now and row["ON/OFF"] == "ON":
            mastodon.toot(row["멘트"])

# 마스토돈 멘션 감지
class ProfessorListener(StreamListener):
    def __init__(self):
        self.sheet = connect_to_sheet()

    def on_notification(self, notification):
        if notification["type"] == "mention":
            content = notification["status"]["content"]
            user_id = notification["account"]["acct"].split("@")[0]
            status_id = notification["status"]["id"]

            if "[등록/" in content:
                name = content.split("[등록/")[1].split("]")[0].strip()
                if name:
                    player_tab = self.sheet.worksheet("플레이어")
                    records = player_tab.get_all_records()
                    for row in records:
                        if row["ID"] == user_id:
                            reply = respond("등록중복").format(name=name)
                            mastodon.status_post(f"@{user_id} {reply}", in_reply_to_id=status_id, visibility="unlisted")
                            return
                    next_row = len(records) + 2
                    player_tab.update(f"A{next_row}:E{next_row}", [[name, user_id, 0, "", 0]])
                    reply = respond("등록완료").format(name=name)
                    mastodon.status_post(f"@{user_id} {reply}", in_reply_to_id=status_id, visibility="unlisted")
                    return

            elif "[출석]" in content:
                reply = handle_attendance(self.sheet, user_id)
                mastodon.status_post(f"@{user_id} {reply}", in_reply_to_id=status_id, visibility="unlisted")
            elif "[과제]" in content:
            elif "[주머니]" in content:
                handle_inventory_request(self.sheet, mastodon, user_id, status_id)

                reply = handle_homework(self.sheet, user_id)
                mastodon.status_post(f"@{user_id} {reply}", in_reply_to_id=status_id, visibility="unlisted")


# [주머니] 기능: 갈레온 + 인벤토리 확인
def split_and_post_response(text, mastodon, acct, in_reply_to_id):
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    prev_id = in_reply_to_id
    for chunk in chunks:
        status = mastodon.status_post(f"@{acct} {chunk}", in_reply_to_id=prev_id, visibility="unlisted")
        prev_id = status["id"]

def handle_inventory_request(sheet, mastodon, acct, in_reply_to_id):
    player_tab = sheet.worksheet("플레이어")
    records = player_tab.get_all_records()
    for row in records:
        if row["ID"] == acct:
            galleon = row.get("갈레온", 0)
            items = row.get("인벤토리", "")
            items_text = items if items else "없음"
            message = f"현재 보유 갈레온: {galleon}\n인벤토리: {items_text}"
            split_and_post_response(message, mastodon, acct, in_reply_to_id)
            return
    mastodon.status_post(f"@{acct} 등록된 유저가 아닙니다.", in_reply_to_id=in_reply_to_id, visibility="unlisted")


def main():
    print("🎓 교수봇이 마스토돈을 실시간 감시 중입니다...")
    sheet = connect_to_sheet()
    while True:
        try:
            send_scheduled_message(sheet)
            time.sleep(60)
        except Exception as e:
            print("자동 멘트 오류:", e)
            time.sleep(10)

if __name__ == "__main__":
    import threading
    threading.Thread(target=main).start()
    mastodon.stream_user(ProfessorListener())
