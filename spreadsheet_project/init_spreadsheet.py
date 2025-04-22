from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime

SPREADSHEET_ID = '1XMmAiO82XYduO_2uTgwFpGbOiieVaDAptNI3MM_a128'

def connect_to_sheets():
    """구글 시트 연결"""
    try:
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = Credentials.from_service_account_file(
            'credentials.json',
            scopes=scopes
        )
        return gspread.authorize(credentials)
    except Exception as e:
        print(f"Google Sheets 연결 중 오류 발생: {str(e)}")
        raise

def get_or_create_sheet(spreadsheet, sheet_name):
    """시트가 없으면 생성하고, 있으면 가져오기"""
    try:
        return spreadsheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(sheet_name, 1000, 26)

def update_sheet_headers(sheet, headers):
    """시트 헤더 업데이트"""
    sheet.clear()  # 기존 데이터 삭제
    sheet.append_row(headers)
    sheet.columns_auto_resize(0, len(headers))

def init_spreadsheet():
    """스프레드시트 초기화 및 데이터 채우기"""
    gc = connect_to_sheets()
    spreadsheet = gc.open_by_key(SPREADSHEET_ID)
    
    # 캐릭터정보 시트 초기화
    character_sheet = get_or_create_sheet(spreadsheet, '캐릭터정보')
    character_headers = [
        '유저ID', '갈레온', '출석횟수', '최대체력', '현재체력',
        '지능', '의지', '매력', '민첩', '공격', '마력'
    ]
    update_sheet_headers(character_sheet, character_headers)
    
    # 상점 시트 초기화
    shop_sheet = get_or_create_sheet(spreadsheet, '상점')
    shop_headers = ['이름', '가격', '설명', '사용가능여부', '카테고리']
    update_sheet_headers(shop_sheet, shop_headers)
    
    # 예시 상점 아이템 추가
    shop_items = [
        ['기본 지팡이', '10', '기본적인 마법 지팡이입니다', 'TRUE', '장비'],
        ['기초 마법서', '5', '마법의 기초를 배울 수 있는 책입니다', 'TRUE', '소모품'],
        ['체력 물약', '3', '체력을 회복시켜주는 물약입니다', 'TRUE', '소모품']
    ]
    for item in shop_items:
        shop_sheet.append_row(item)

def main():
    try:
        print("Google Sheets에 연결 중...")
        gc = connect_to_sheets()
        print("연결 성공!")

        print(f"스프레드시트 ID {SPREADSHEET_ID}를 여는 중...")
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        print("스프레드시트를 열었습니다!")

        # 스프레드시트 초기화
        init_spreadsheet()
        
    except Exception as e:
        print(f"오류가 발생했습니다: {str(e)}")
        raise

if __name__ == "__main__":
    main()


