
import os
import re
import random
from mastodon import Mastodon
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

# 마스토돈 연결
mastodon = Mastodon(
    access_token=os.getenv("MASTODON_ACCESS_TOKEN"),
    api_base_url=os.getenv("MASTODON_BASE_URL")
)

# 구글 시트 연결
def connect_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv("GOOGLE_CREDENTIALS_JSON"), scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID"))
    return sheet.worksheet("플레이어"), sheet.worksheet("shop_items"), sheet.worksheet("settings")

# 상점 응답
def get_shop_list(shop_sheet):
    records = shop_sheet.get_all_records()
    lines = ["📦 상점 아이템 목록:"]
    for row in records:
        lines.append(f"- {row['아이템명']} ({row['설명']}) - 💰{row['가격']}G")
    return "\n".join(lines)

# 아이템 구매
def buy_item(player_sheet, shop_sheet, user_id, item_name):
    player_data = player_sheet.get_all_records()
    shop_data = shop_sheet.get_all_records()

    for player_index, row in enumerate(player_data):
        if row["ID"] == user_id:
            for item in shop_data:
                if item["아이템명"] == item_name:
                    price = int(item["가격"])
                    if row["갈레온"] >= price:
                        row["갈레온"] -= price
                        inventory = row["인벤토리"].split(",") if row["인벤토리"] else []
                        inventory.append(item_name)
                        player_sheet.update_cell(player_index + 2, 3, row["갈레온"])
                        player_sheet.update_cell(player_index + 2, 4, ",".join(inventory))
                        return f"{item_name} 구매 완료! (-{price}G)"
                    else:
                        return "갈레온이 부족합니다."
            return "상점에 해당 아이템이 없습니다."
    return "등록된 유저가 아닙니다."

# 아이템 판매
def sell_item(player_sheet, shop_sheet, user_id, item_name):
    player_data = player_sheet.get_all_records()
    shop_data = shop_sheet.get_all_records()

    for player_index, row in enumerate(player_data):
        if row["ID"] == user_id:
            inventory = row["인벤토리"].split(",") if row["인벤토리"] else []
            if item_name in inventory:
                for item in shop_data:
                    if item["아이템명"] == item_name:
                        price = int(item["되파는가격"])
                        inventory.remove(item_name)
                        row["갈레온"] += price
                        player_sheet.update_cell(player_index + 2, 3, row["갈레온"])
                        player_sheet.update_cell(player_index + 2, 4, ",".join(inventory))
                        return f"{item_name} 판매 완료! (+{price}G)"
            return "인벤토리에 해당 아이템이 없습니다."
    return "등록된 유저가 아닙니다."

# [주머니] 기능
def handle_inventory_request(sheet, mastodon, acct, in_reply_to_id):
    records = sheet.get_all_records()
    for row in records:
        if row["ID"] == acct:
            galleon = row.get("갈레온", 0)
            items = row.get("인벤토리", "")
            items_text = items if items else "없음"
            message = f"현재 보유 갈레온: {galleon}\n인벤토리: {items_text}"
            split_and_post_response(message, mastodon, acct, in_reply_to_id)
            return
    mastodon.status_post(f"@{acct} 등록된 유저가 아닙니다.", in_reply_to_id=in_reply_to_id, visibility="unlisted")

# 운세 기능
def get_daily_fortune():
    fortunes = [
        "오늘은 조용히 지나갈 거예요.",
        "무언가 반짝이는 걸 발견할지도 몰라요!",
        "조심하세요, 예기치 못한 변화가 있을 수 있어요.",
        "좋은 일이 생길 거예요. 조금만 기다려보세요.",
        "옛 친구의 말이 마음에 남을지도 몰라요."
    ]
    return random.choice(fortunes)

# 행운주머니 기능
def lucky_pouch(player_sheet, settings_sheet, user_id):
    min_val = get_setting(settings_sheet, "행운주머니_최소값")
    max_val = get_setting(settings_sheet, "행운주머니_최대값")
    diff = random.randint(min_val, max_val)
    update_player_galleon(player_sheet, user_id, diff)
    return f"행운주머니를 열어보니 {diff:+} 갈레온의 변화가 생겼습니다!"

# 주사위 굴리기
def roll_dice(key, settings_sheet):
    face_count = get_setting(settings_sheet, key)
    if face_count:
        result = random.randint(1, face_count)
        return f"{key} 결과: 🎲 {result}"
    return "해당 주사위 설정이 없습니다."

# 설정 값 가져오기
def get_setting(sheet, key):
    records = sheet.get_all_records()
    for row in records:
        if row["설정항목"] == key:
            return int(row["값"])
    return None

# [상점] 처리
def get_shop_list(shop_sheet):
    records = shop_sheet.get_all_records()
    lines = ["📦 상점 아이템 목록:"]
    for row in records:
        lines.append(f"- {row['아이템명']} ({row['설명']}) - 💰{row['가격']}G")
    return "\n".join(lines)

# [시전 마법] 처리 함수
def cast_spell(player_sheet, spell_sheet, caster_id, target_id, spell_name, players_data):
    caster_row = next((row for row in players_data if row["ID"] == caster_id), None)
    target_row = next((row for row in players_data if row["ID"] == target_id), None)

    if not caster_row:
        return "시전자가 등록되어 있지 않습니다."
    if not target_row and target_id:
        return "대상이 존재하지 않습니다."

    # 마법 정보 불러오기
    spells = spell_sheet.get_all_records()
    spell = next((s for s in spells if s["마법명"] == spell_name), None)

    if not spell:
        return f"{spell_name} 마법은 존재하지 않습니다."

    mp_cost = int(spell["MP소모"])
    if caster_row["MP"] < mp_cost:
        return "마나가 부족합니다."

    # 판정 방식 해석 (간단한 예)
    if spell["판정방식"] == "MAG vs WIL":
        caster_score = caster_row["마력"] + random.randint(1, 20)
        target_score = target_row["의지"] + random.randint(1, 20)
    elif spell["판정방식"] == "INT + MAG vs 난이도":
        caster_score = caster_row["지능"] + caster_row["마력"] + random.randint(1, 20)
        target_score = int(spell.get("난이도", 15))  # 기본 난이도 15
    else:
        return "판정 방식을 해석할 수 없습니다."

    # MP 차감
    row_index = players_data.index(caster_row) + 2  # header 제외
    caster_row["MP"] -= mp_cost
    player_sheet.update_cell(row_index, 8, caster_row["MP"])

    # 판정 결과
    if caster_score > target_score:
        return f"✨ {spell['마법명']} 성공! ({spell['성공효과']})"
    else:
        return f"⚡ {spell['마법명']} 실패! 효과 없음."

# 멘션 감지
class ShopListener(StreamListener):
    def __init__(self):
        self.player_sheet, self.shop_sheet, self.settings_sheet = connect_sheets()

    def on_notification(self, notification):
        if notification["type"] == "mention":
            content = notification["status"]["content"]
            acct = notification["account"]["acct"]
            status_id = notification["status"]["id"]

            if "[상점]" in content:
                text = get_shop_list(self.shop_sheet)
                mastodon.status_post(f"@{acct} {text}", in_reply_to_id=status_id, visibility="unlisted")

            elif "[구매" in content:
                match = re.search(r"\[구매 (.+?)\]", content)
                if match:
                    item = match.group(1).strip()
                    result = buy_item(self.player_sheet, self.shop_sheet, acct, item)
                    mastodon.status_post(f"@{acct} {result}", in_reply_to_id=status_id, visibility="unlisted")

            elif "[판매" in content:
                match = re.search(r"\[판매 (.+?)\]", content)
                if match:
                    item = match.group(1).strip()
                    result = sell_item(self.player_sheet, self.shop_sheet, acct, item)
                    mastodon.status_post(f"@{acct} {result}", in_reply_to_id=status_id, visibility="unlisted")

            elif "[주머니]" in content:
                handle_inventory_request(self.player_sheet, mastodon, acct, status_id)

            elif "[운세]" in content:
                result = get_daily_fortune()
                mastodon.status_post(f"@{acct} {result}", in_reply_to_id=status_id, visibility="unlisted")

            elif "[행운주머니]" in content:
                result = lucky_pouch(self.player_sheet, self.settings_sheet, acct)
                mastodon.status_post(f"@{acct} {result}", in_reply_to_id=status_id, visibility="unlisted")

            elif "[주사위]" in content:
                result = roll_dice("주사위_d6", self.settings_sheet)
                mastodon.status_post(f"@{acct} {result}", in_reply_to_id=status_id, visibility="unlisted")

            elif "[d12]" in content:
                result = roll_dice("주사위_d12", self.settings_sheet)
                mastodon.status_post(f"@{acct} {result}", in_reply_to_id=status_id, visibility="unlisted")

            elif "[d20]" in content:
                result = roll_dice("주사위_d20", self.settings_sheet)
                mastodon.status_post(f"@{acct} {result}", in_reply_to_id=status_id, visibility="unlisted")

            elif "[시전" in content:
                match = re.search(r"\[시전 (.+?) @(.+?)\]", content)
                if match:
                    spell_name = match.group(1).strip()
                    target_name = match.group(2).strip()
                    result = cast_spell(self.player_sheet, self.shop_sheet, acct, target_name, spell_name, self.players_data)
                    mastodon.status_post(f"@{acct} {result}", in_reply_to_id=status_id, visibility="unlisted")

if __name__ == "__main__":
    print("🛍️ 상점 봇 실행 중...")
    mastodon.stream_user(ShopListener())
