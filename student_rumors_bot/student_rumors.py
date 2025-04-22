from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime

def _init_riley_rumors_sheet(self, spreadsheet):
    """라일리 관련 소문 시트 초기화"""
    headers = ['NPC이름', '소속', '학년', '성격', '라일리 관련 소문', '신뢰도', '활성화']
    try:
        rumors_sheet = spreadsheet.worksheet('라일리_소문')
    except:
        rumors_sheet = spreadsheet.add_worksheet('라일리_소문', 100, len(headers))
    
    rumors_sheet.update('A1:G1', [headers])
    
    # 1992년 시점의 라일리(당시 3학년) 관련 소문들
    riley_rumors = [
        # 고학년 (6-7학년) - 실종 전부터 라일리를 알았던 선배들
        ['에드워드 나이트', '래번클로', '7학년', '관찰력 있고 신중한', 
         '라일리가 도서관 금서 구역에서 뭔가를 찾고 있었어. 항상 혼자서...', '높음', 'TRUE'],
        ['세라피나 블랙', '슬리데린', '6학년', '차갑고 날카로운', 
         '3학년치고는 너무 뛰어난 실력이었지. 특히 기억과 관련된 마법에서...', '높음', 'TRUE'],
        
        # 중간 학년 (3-4학년) - 라일리와 같은 시기 학생들
        ['올리버 우드', '그리핀도르', '4학년', '정직하고 단순한', 
         '며칠 전까지 수업에서 봤는데... 갑자기 사라졌어. 이상하지 않아?', '중간', 'TRUE'],
        ['헬레나 로즈', '후플푸프', '3학년', '따뜻하고 공감적인', 
         '라일리는 항상 도서관 구석에서 혼자 책을 읽었어. 마지막으로 본 게 언제였더라...', '중간', 'TRUE'],
        
        # 저학년 (1-2학년) - 소문으로만 듣는 학생들
        ['마커스 플린트', '슬리데린', '2학년', '거칠고 단순한', 
         '선배들이 그러는데, 밤에 천문탑에서 뭔가 있었대. 추락사고라나...', '낮음', 'TRUE'],
        ['페넬로페 문', '래번클로', '1학년', '호기심 많은', 
         '도서관에서 이상한 책을 보다가... 그러니까, 그게 금지된 마법이었대.', '낮음', 'TRUE'],
        
        # 특별한 목격자
        ['칼럼', '래번클로', '3학년', '조용하고 수수께끼 같은', 
         '(묵묵부답... 하지만 무언가를 알고 있는 듯한 눈빛)', '알 수 없음', 'TRUE']
    ]
    rumors_sheet.update('A2:G8', riley_rumors)



class NPCManager:
    def __init__(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id
        self.gc = self._connect_to_sheets()
        self.last_update = 0
        self.update_interval = 5
        self.npcs = {}
        
    def _connect_to_sheets(self):
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = Credentials.from_service_account_file(
            'credentials.json',
            scopes=scopes
        )
        return gspread.authorize(credentials)

    def _update_npcs(self):
        """NPC 정보 갱신"""
        current_time = datetime.now().timestamp()
        if current_time - self.last_update > self.update_interval:
            try:
                sheet = self.gc.open_by_key(self.spreadsheet_id).worksheet('NPC목록')
                data = sheet.get_all_values()[1:]  # 헤더 제외
                
                self.npcs = {}
                for row in data:
                    if len(row) >= 6 and row[5].upper() == 'TRUE':
                        name, personality, affiliation, description, topics, _ = row[:6]
                        self.npcs[name] = {
                            'personality': personality,
                            'affiliation': affiliation,
                            'description': description,
                            'topics': [t.strip() for t in topics.split(',')]
                        }
                
                self.last_update = current_time
            except Exception as e:
                print(f"NPC 데이터 갱신 중 오류: {str(e)}")

    def log_conversation(self, npc_name, user_id, dialogue, emotion='일반'):
        """대화 내용 기록"""
        try:
            sheet = self.gc.open_by_key(self.spreadsheet_id).worksheet('대화로그')
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sheet.append_row([now, npc_name, user_id, dialogue, emotion])
            return True
        except Exception as e:
            print(f"대화 로그 기록 중 오류: {str(e)}")
            return False

    def get_npc_data(self, npc_name):
        """NPC 데이터 조회 (내부 사용)"""
        self._update_npcs()
        return self.npcs.get(npc_name)

    def is_valid_npc(self, npc_name):
        """유효한 NPC인지 확인"""
        return npc_name in self.npcs

