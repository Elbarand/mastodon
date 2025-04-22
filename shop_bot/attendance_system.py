from datetime import datetime, time
import random
import gspread
from google.oauth2.credentials import Credentials

class RewardSystem:
    def __init__(self, spreadsheet_id, character_manager):
        self.attendance_history = {}  # {user_id: datetime}
        self.assignment_count = {}    # {user_id: count}
        self.start_time = time(9, 0)  # 오전 9시
        self.end_time = time(22, 0)   # 밤 10시
        self.attendance_reward = 2
        self.assignment_reward = 5
        self.max_assignments = 4

        # 구글 스프레드시트 초기화
        self.spreadsheet_id = spreadsheet_id
        self.gc = self._init_google_sheets()
        self.settings_sheet = self.gc.open_by_key(spreadsheet_id).worksheet('설정')
        
        # 캐릭터 매니저 연결
        self.character_manager = character_manager
        
        # 시스템 상태 초기화
        self.attendance_active = False
        self.assignment_active = False
        self.update_system_status()
        
        self.praise_messages = [
            "훌륭해요! 오늘도 열심히 공부하는 모습이 보기 좋네요. 2갈레온을 드리겠습니다!",
            "좋은 아침이에요! 일찍 일어난 당신에게 2갈레온을 드립니다!",
            "오늘도 성실하게 출석하셨네요. 2갈레온을 받으세요!",
            "학구열이 대단하군요! 여기 2갈레온이 있습니다.",
            "밝은 모습으로 출석해주셔서 감사해요. 2갈레온을 드리겠습니다!",
            "오늘도 열정적인 모습이네요! 2갈레온을 받으세요.",
            "시간을 잘 지키는 당신! 2갈레온의 주인공입니다.",
            "성실한 태도가 보기 좋습니다. 2갈레온을 드려요!",
            "출석체크 완료! 오늘도 좋은 하루 되세요. 2갈레온 받으세요~",
            "학생의 본분을 잘 지키고 계시네요. 2갈레온을 드립니다!"
        ]
        
        self.assignment_messages = [
            "훌륭한 과제입니다! 5갈레온을 드리겠습니다!",
            "과제 제출 감사합니다. 열심히 하는 모습이 보기 좋네요. 5갈레온을 받으세요!",
            "뛰어난 과제군요! 보상으로 5갈레온을 드립니다.",
            "성실한 과제 수행이 돋보입니다. 5갈레온을 지급해드릴게요!",
            "과제를 잘 완수하셨네요. 5갈레온을 받으세요!"
        ]
        
        self.late_night_messages = [
            "이제 주무실 시간이에요. 내일 아침에 다시 만나요!",
            "출석 체크는 내일 아침 9시부터 다시 시작됩니다. 좋은 밤 되세요!",
            "밤이 깊었네요. 충분한 휴식을 취하고 내일 뵙겠습니다!",
            "건강을 위해 이제 주무세요. 내일 아침에 뵙겠습니다!",
            "출석 시간이 끝났어요. 내일 더 활기찬 모습으로 만나요!"
        ]

    def _init_google_sheets(self):
        """구글 시트 초기 연결 설정"""
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = Credentials.from_service_account_file(
            'credentials.json',
            scopes=scopes
        )
        return gspread.authorize(credentials)

    def update_system_status(self):
        """스프레드시트에서 시스템 상태를 업데이트합니다"""
        try:
            # B2: 출석 시스템 상태, B3: 과제 시스템 상태
            self.attendance_active = self.settings_sheet.acell('B2').value == '활성화'
            self.assignment_active = self.settings_sheet.acell('B3').value == '활성화'
        except Exception as e:
            print(f"시스템 상태 업데이트 중 오류 발생: {e}")

    def check_attendance(self, user_id):
        """출석을 체크하고 갈레온을 자동으로 지급합니다."""
        # 시스템 상태 확인
        self.update_system_status()
        if not self.attendance_active:
            return "현재 출석 시스템이 비활성화되어 있습니다.", 0

        current_time = datetime.now().time()
        
        if current_time < self.start_time:
            return "아직 출석 시간이 아닙니다. 오전 9시부터 출석을 시작합니다!", 0
        
        if current_time >= self.end_time:
            return random.choice(self.late_night_messages), 0

        today = datetime.now().date()
        if user_id in self.attendance_history:
            last_attendance = self.attendance_history[user_id].date()
            if last_attendance == today:
                return "이미 오늘은 출석체크를 하셨습니다!", 0

        self.attendance_history[user_id] = datetime.now()
        
        # 캐릭터 시트 업데이트
        self.character_manager.add_galleons(user_id, self.attendance_reward)
        self.character_manager.increment_attendance(user_id)
        
        return random.choice(self.praise_messages), self.attendance_reward

    def submit_assignment(self, user_id):
        """과제를 제출하고 갈레온을 자동으로 지급합니다."""
        # 시스템 상태 확인
        self.update_system_status()
        if not self.assignment_active:
            return "현재 과제 시스템이 비활성화되어 있습니다.", 0

        if user_id not in self.assignment_count:
            self.assignment_count[user_id] = 0
            
        if self.assignment_count[user_id] >= self.max_assignments:
            return "이번 학기 과제 제출 횟수를 모두 사용하셨습니다.", 0
            
        self.assignment_count[user_id] += 1
        
        # 캐릭터 시트 업데이트
        self.character_manager.add_galleons(user_id, self.assignment_reward)
        
        remaining = self.max_assignments - self.assignment_count[user_id]
        message = f"{random.choice(self.assignment_messages)}\n남은 과제 제출 기회: {remaining}회"
        
        return message, self.assignment_reward

class UserData:
    def __init__(self):
        self.galleons = 0

# 시스템 초기화
SPREADSHEET_ID = '여기에_스프레드시트_ID_입력'
reward_system = RewardSystem(SPREADSHEET_ID)

def handle_message(user_id, user_data, message_content):
    """메시지를 처리하고 적절한 보상을 지급합니다."""
    if "출석" in message_content:
        message, galleons = reward_system.check_attendance(user_id)
    elif "과제" in message_content:
        message, galleons = reward_system.submit_assignment(user_id)
    else:
        return None

    if galleons > 0:
        return f"{message}\n현재 보유 갈레온: {user_data.galleons}"
    
    return message

# 사용자 데이터 초기화
user_data = UserData()

# 출석 체크
response = handle_message("user123", user_data, "출석")
print(response)  # 출석 메시지와 2갈레온 지급

# 과제 제출
response = handle_message("user123", user_data, "과제")
print(response)  # 과제 제출 메시지, 5갈레온 지급, 남은 기회 표시

# 출석 체크 테스트
message = "출석"
response = handle_message("user123", user_data, message)
print(response)  # 출석 메시지와 현재 갈레온 수가 표시됨







