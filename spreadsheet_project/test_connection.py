import gspread
from google.oauth2.service_account import Credentials
import sys

def test_connection():
    print("1. 테스트를 시작합니다...")
    
    try:
        print("2. 사용할 라이브러리 버전:")
        print(f"Python 버전: {sys.version}")
        print(f"gspread 버전: {gspread.__version__}")
        
        print("\n3. API 연결 시도 중...")
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        print("4. credentials.json 파일을 읽는 중...")
        credentials = Credentials.from_service_account_file(
            'credentials.json',
            scopes=scopes
        )

        print("5. 스프레드시트 연결 중...")
        gc = gspread.authorize(credentials)
        spreadsheet = gc.open_by_key('1XMmAiO82XYduO_2uTgwFpGbOiieVaDAptNI3MM_a128')
        
        print("6. 현재 시트 목록:")
        for worksheet in spreadsheet.worksheets():
            print(f"   - {worksheet.title}")
        
        print("\n7. 테스트 완료! 연결이 성공적으로 이루어졌습니다.")
        
    except FileNotFoundError:
        print("오류: credentials.json 파일을 찾을 수 없습니다!")
        import os
        print("현재 실행 위치:", os.getcwd())
    except Exception as e:
        print("오류가 발생했습니다:", str(e))
        print("오류 타입:", type(e).__name__)

if __name__ == "__main__":
    test_connection()


