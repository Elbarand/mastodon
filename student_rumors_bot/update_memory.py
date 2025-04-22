import os
import datetime
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from dotenv import load_dotenv

load_dotenv()

# 구글 시트 연동
def connect_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv("GOOGLE_CREDENTIALS_JSON"), scope)
    client = gspread.authorize(creds)
    return client.open_by_key(os.getenv("GOOGLE_SHEET_ID")).worksheet("npc_data")

# 기억 상태 변화 규칙
def update_memory_state(current_state, days_elapsed):
    if current_state == "명확":
        if days_elapsed >= 9:
            return "왜곡"
        elif days_elapsed >= 6:
            return "흐릿"
        elif days_elapsed >= 3:
            return "흐릿"
    elif current_state == "흐릿":
        if days_elapsed >= 8:
            return "없음"
        elif days_elapsed >= 5:
            return "없음"
    elif current_state == "왜곡":
        if days_elapsed >= 10:
            return "없음"
    return current_state

# 기억 내용도 간단히 바꿈
def update_memory_content(state):
    if state == "흐릿":
        return "희미하게 무엇인가 본 것 같다고 말함"
    elif state == "없음":
        return "기억나지 않는다고 말함"
    elif state == "왜곡":
        return "사실은 유령이었다고 주장함"
    else:
        return ""  # 명확한 경우는 기존 내용 유지

# 시트에서 불러와 갱신 후 다시 저장
def update_npc_memory():
    sheet = connect_sheet()
    records = sheet.get_all_records()
    today = datetime.date.today()

    for i, row in enumerate(records):
        name = row["이름"]
        current_state = row["기억 상태"]
        last_update_str = row["마지막 갱신일"]
        last_update = datetime.datetime.strptime(last_update_str, "%Y-%m-%d").date()
        days_elapsed = (today - last_update).days

        new_state = update_memory_state(current_state, days_elapsed)
        if new_state != current_state:
            # 상태 바뀐 경우만 갱신
            memory_content = update_memory_content(new_state)
            sheet.update_cell(i+2, 4, new_state)
            if memory_content:
                sheet.update_cell(i+2, 5, memory_content)
            sheet.update_cell(i+2, 14, today.strftime("%Y-%m-%d"))
            print(f"{name}의 기억이 '{current_state}' → '{new_state}' 로 변경됨")

if __name__ == "__main__":
    update_npc_memory()
