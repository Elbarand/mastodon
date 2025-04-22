from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime

def write_to_sheets():
    try:
        print("1. 인증 시작...")
        CREDENTIALS_PATH = r'C:\Users\USER\.ssh\elbarand\spreadsheet_project\credentials.json'
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = Credentials.from_service_account_file(
            CREDENTIALS_PATH,
            scopes=scopes
        )
        print("2. 인증 완료")
        
        # Google Sheets 연결
        print("3. 스프레드시트 연결 시도...")
        gc = gspread.authorize(credentials)
        SPREADSHEET_ID = '1XMmAiO82XYduO_2uTgwFpGbOiieVaDAptNI3MM_a128'
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        print("4. 스프레드시트 연결 완료")
        
        # 모든 워크시트 정보 출력
        print("\n현재 스프레드시트의 모든 시트 목록:")
        worksheets = spreadsheet.worksheets()
        for ws in worksheets:
            print(f"- 시트 제목: {ws.title}, ID: {ws.id}")
        
        # gid로 특정 시트 선택
        print("\n5. 워크시트 선택 중...")
        worksheet = spreadsheet.get_worksheet_by_id(1307690060)  # 캐릭터정보 시트
        print(f"6. 선택된 워크시트 제목: {worksheet.title}")
        
        # 데이터 쓰기
        print("7. 데이터 쓰기 시도...")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 캐릭터정보 시트의 형식에 맞게 데이터 구성
        data = ['USER123', 100, 1, 100, 100, 10, 10, 10, 10, 10, 10]  # 예시 데이터
        worksheet.append_row(data)
        print(f"8. 데이터 쓰기 완료: {current_time}")
        
        # 확인을 위해 마지막 행 읽기
        print("9. 마지막 행 확인 중...")
        last_row = worksheet.get_all_values()[-1]
        print(f"10. 마지막 행 데이터: {last_row}")
        
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        print(f"오류 타입: {type(e).__name__}")

if __name__ == "__main__":
    write_to_sheets()




