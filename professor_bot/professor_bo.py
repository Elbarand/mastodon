from datetime import datetime, time
import schedule
import threading
import time as time_module
import gspread
from google.oauth2.credentials import Credentials

class CurfewSystem:
    def __init__(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id
        self.gc = self._init_google_sheets()
        self.worksheet = self.gc.open_by_key(spreadsheet_id).worksheet('설정')
        self.is_active = self._get_system_status()
        
        self.curfew_start = time(2, 0)  # 새벽 2시
        self.curfew_end = time(6, 0)    # 아침 6시
        
        self.curfew_messages = [
            "🌙 통금 시간입니다! (새벽 2시 ~ 6시)\n충분한 휴식을 취하고 내일 더 활기찬 모습으로 만나요!",
            "🌙 이제 통금 시간이에요. 건강을 위해 꼭 쉬어주세요!",
            "🌙 통금이 시작되었습니다. 달빛 아래 편안한 밤 되세요~"
        ]
        
        self.wake_up_messages = [
            "🌅 좋은 아침입니다! 통금이 해제되었어요.\n새로운 하루를 시작해볼까요?",
            "🌅 통금이 끝났습니다! 상쾌한 아침과 함께 시작하는 마법 수업!",
            "🌅 통금 해제! 일찍 일어난 당신, 오늘도 멋진 하루 보내세요!"
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

    def _get_system_status(self):
        """스프레드시트에서 시스템 상태를 가져옵니다"""
        try:
            status = self.worksheet.acell('B1').value
            return status == '활성화'  # '활성화'면 True, '비활성화'면 False 반환
        except Exception as e:
            print(f"시스템 상태 확인 중 오류 발생: {e}")
            return False

    def check_and_update_status(self):
        """시스템 상태를 주기적으로 확인하고 업데이트합니다"""
        new_status = self._get_system_status()
        if new_status != self.is_active:
            self.is_active = new_status
            status_str = '활성화' if self.is_active else '비활성화'
            print(f"통금 시스템 상태가 변경되었습니다: {status_str}")
        
    def get_random_message(self, is_curfew_start):
        """랜덤한 메시지를 반환합니다."""
        import random
        messages = self.curfew_messages if is_curfew_start else self.wake_up_messages
        return random.choice(messages)
        
    def is_curfew_time(self):
        """현재 통금 시간인지 확인합니다."""
        current_time = datetime.now().time()
        if self.curfew_start <= self.curfew_end:
            return self.curfew_start <= current_time <= self.curfew_end
        else:
            return current_time >= self.curfew_start or current_time <= self.curfew_end

    def schedule_announcements(self):
        """통금 시작과 해제 알림을 스케줄링합니다."""
        def curfew_start_announcement():
            self.check_and_update_status()
            if self.is_active:
                return self.get_random_message(True)
            
        def curfew_end_announcement():
            self.check_and_update_status()
            if self.is_active:
                return self.get_random_message(False)
        
        schedule.every().day.at("02:00").do(curfew_start_announcement)
        schedule.every().day.at("06:00").do(curfew_end_announcement)
        # 5분마다 시스템 상태 확인
        schedule.every(5).minutes.do(self.check_and_update_status)

    def run_scheduler(self):
        """스케줄러를 백그라운드에서 실행합니다."""
        def run():
            while True:
                schedule.run_pending()
                time_module.sleep(60)
                
        scheduler_thread = threading.Thread(target=run, daemon=True)
        scheduler_thread.start()

def handle_curfew_command(command):
    """통금 시스템 명령어를 처리합니다."""
    if command == "통금상태":
        status = "활성화" if curfew_system.is_active else "비활성화"
        return f"현재 통금 시스템이 {status} 상태입니다."
    elif command == "통금시간":
        if curfew_system.is_curfew_time():
            return "현재는 통금 시간입니다. (새벽 2시 ~ 6시)"
        else:
            return "현재는 통금 시간이 아닙니다."

# 시스템 초기화 및 실행
SPREADSHEET_ID = '여기에_스프레드시트_ID_입력'
curfew_system = CurfewSystem(SPREADSHEET_ID)
curfew_system.schedule_announcements()
curfew_system.run_scheduler()

class CharacterManager:
    def __init__(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id
        self.gc = self._init_google_sheets()
        self.sheet = self.gc.open_by_key(spreadsheet_id).worksheet('Characters')
        self.character_cache = {}
        self.last_refresh = None
        self.cache_duration = 300  # 5분 캐시

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

    def refresh_cache(self):
        """캐릭터 데이터 캐시 새로고침"""
        current_time = datetime.now()
        if (self.last_refresh is None or 
            (current_time - self.last_refresh).seconds > self.cache_duration):
            
            all_records = self.sheet.get_all_records()
            self.character_cache = {
                record['user_id']: {
                    'galleons': record['galleons'],
                    'attendance_count': record['attendance_count'],
                    'max_hp': record['max_hp'],
                    'current_hp': record['current_hp'],
                    'adult_class': record.get('전문직', ''),  # 성인 클래스 필드
                    'status': {
                        'INT': record['INT'],
                        'WIL': record['WIL'],
                        'CHA': record['CHA'],
                        'DEX': record['DEX'],
                        'STR': record['STR'],
                        'MAG': record['MAG']
                    }
                }
                for record in all_records
            }
            self.last_refresh = current_time

    def get_character(self, user_id):
        """캐릭터 정보 조회"""
        self.refresh_cache()
        return self.character_cache.get(user_id)

    def update_character(self, user_id, updates):
        """캐릭터 정보 업데이트"""
        try:
            # 해당 유저의 행 찾기
            cell = self.sheet.find(user_id)
            if not cell:
                # 새 캐릭터 생성
                return self.create_character(user_id, updates)

            row = cell.row
            
            # 업데이트할 필드와 값 준비
            for field, value in updates.items():
                if field == 'status':
                    # 스테이터스 개별 업데이트
                    for stat, stat_value in value.items():
                        col = self.get_column_index(stat)
                        self.sheet.update_cell(row, col, stat_value)
                else:
                    # 일반 필드 업데이트
                    col = self.get_column_index(field)
                    self.sheet.update_cell(row, col, value)

            # 캐시 무효화
            self.last_refresh = None
            return True

        except Exception as e:
            print(f"캐릭터 업데이트 중 오류 발생: {e}")
            return False

    def create_character(self, user_id, initial_data):
        """새 캐릭터 생성"""
        try:
            # 기본값 설정
            default_data = {
                'user_id': user_id,
                'galleons': initial_data.get('galleons', 0),
                'attendance_count': initial_data.get('attendance_count', 0),
                'max_hp': initial_data.get('max_hp', 100),
                'current_hp': initial_data.get('current_hp', 100),
                'INT': initial_data.get('status', {}).get('INT', 10),
                'WIL': initial_data.get('status', {}).get('WIL', 10),
                'CHA': initial_data.get('status', {}).get('CHA', 10),
                'DEX': initial_data.get('status', {}).get('DEX', 10),
                'STR': initial_data.get('status', {}).get('STR', 10),
                'MAG': initial_data.get('status', {}).get('MAG', 10)
            }

            # 새 행 추가
            self.sheet.append_row(list(default_data.values()))
            
            # 캐시 무효화
            self.last_refresh = None
            return True

        except Exception as e:
            print(f"캐릭터 생성 중 오류 발생: {e}")
            return False

    def get_column_index(self, field_name):
        """필드 이름에 해당하는 열 인덱스 반환"""
        headers = {
            'user_id': 1,      # 유저ID
            'galleons': 2,     # 갈레온
            'attendance_count': 3,  # 출석횟수
            'max_hp': 4,       # 최대체력
            'current_hp': 5,   # 현재체력
            'INT': 6,         # 지능
            'WIL': 7,         # 의지
            'CHA': 8,         # 매력
            'DEX': 9,         # 민첩
            'STR': 10,        # 공격
            'MAG': 11         # 마력
        }
        return headers.get(field_name, 1)

    def heal_character(self, user_id, amount):
        """캐릭터 체력 회복"""
        character = self.get_character(user_id)
        if not character:
            return False

        new_hp = min(
            character['current_hp'] + amount,
            character['max_hp']
        )
        
        return self.update_character(user_id, {'current_hp': new_hp})

    def damage_character(self, user_id, amount):
        """캐릭터 체력 감소"""
        character = self.get_character(user_id)
        if not character:
            return False

        new_hp = max(character['current_hp'] - amount, 0)
        return self.update_character(user_id, {'current_hp': new_hp})

    def add_galleons(self, user_id, amount):
        """갈레온 추가"""
        character = self.get_character(user_id)
        if not character:
            return False

        new_galleons = character['galleons'] + amount
        return self.update_character(user_id, {'galleons': new_galleons})

    def increment_attendance(self, user_id):
        """출석 횟수 증가"""
        character = self.get_character(user_id)
        if not character:
            return False

        new_count = character['attendance_count'] + 1
        return self.update_character(user_id, {'attendance_count': new_count})

    def apply_adult_class_bonuses(self, user_id):
        """성인 클래스 보너스 적용"""
        character = self.get_character(user_id)
        if not character:
            return False

        adult_class = character.get('전문직')
        if not adult_class:
            return False

        # 성인 클래스별 보너스 정의
        class_bonuses = {
            '아카이브 헌터': {
                'status': {
                    'INT': 2,
                    'WIL': 1
                },
                'dice_bonus': {
                    'investigation': 1,
                    'research': 1
                }
            },
            '세이버': {
                'status': {
                    'MAG': 2,
                    'STR': 1
                },
                'dice_bonus': {
                    'attack': 1
                }
            },
            '실루엣': {
                'status': {
                    'DEX': 2,
                    'WIL': 2
                },
                'dice_bonus': {
                    'stealth': 1,
                    'acrobatics': 1
                }
            },
            '바인더': {
                'status': {
                    'WIL': 3,
                    'INT': 1
                },
                'dice_bonus': {
                    'binding': 1,
                    'control': 1
                }
            },
            '렉쳐러': {
                'status': {
                    'INT': 3
                },
                'dice_bonus': {
                    'knowledge': 1,
                    'teaching': 1
                }
            }
        }

        # 해당 클래스의 보너스 가져오기
        bonuses = class_bonuses.get(adult_class)
        if not bonuses:
            return False

        # 스테이터스 보너스 적용
        updates = {}
        if 'status' in bonuses:
            current_status = character['status']
            for stat, bonus in bonuses['status'].items():
                current_status[stat] = current_status[stat] + bonus
            updates['status'] = current_status

        # 캐릭터 업데이트
        return self.update_character(user_id, updates)

    def set_adult_class(self, user_id, class_name):
        """성인 클래스 설정"""
        character = self.get_character(user_id)
        if not character:
            return False, "캐릭터를 찾을 수 없습니다."

        # 클래스 요구사항 체크
        requirements = {
            '아카이브 헌터': {
                'INT': 12,
                'WIL': 10
            },
            '세이버': {
                'MAG': 12,
                'STR': 10
            },
            '실루엣': {
                'DEX': 12,
                'WIL': 12
            },
            '바인더': {
                'WIL': 13,
                'INT': 11
            },
            '렉쳐러': {
                'INT': 13
            }
        }

        class_req = requirements.get(class_name)
        if class_req:
            for stat, required_value in class_req.items():
                if character['status'].get(stat, 0) < required_value:
                    return False, f"{stat} 수치가 부족합니다. (필요: {required_value})"

        # 클래스 설정 및 보너스 적용
        updates = {'전문직': class_name}
        if self.update_character(user_id, updates):
            self.apply_adult_class_bonuses(user_id)
            return True, f"{class_name} 직업이 설정되었습니다."
        
        return False, "직업 설정에 실패했습니다."

    def get_available_adult_classes(self, user_id):
        """선택 가능한 성인 클래스 목록 반환"""
        character = self.get_character(user_id)
        if not character:
            return []

        available_classes = []
        status = character['status']

        # 각 클래스별 요구사항 체크
        if status['INT'] >= 12 and status['WIL'] >= 10:
            available_classes.append({
                'name': '아카이브 헌터',
                'description': '잊혀진 기록과 유물을 찾아 진실을 밝히는 조사관',
                'requirements': {
                    'INT': 12,
                    'WIL': 10
                },
                'bonuses': {
                    'INT': 2,
                    'WIL': 1,
                    'dice_bonus': '조사/연구 판정 +1'
                }
            })

        if status['MAG'] >= 12 and status['STR'] >= 10:
            available_classes.append({
                'name': '세이버',
                'description': '마력과 전투 능력을 겸비한 전사',
                'requirements': {
                    'MAG': 12,
                    'STR': 10
                },
                'bonuses': {
                    'MAG': 2,
                    'STR': 1,
                    'dice_bonus': '공격 판정 +1'
                }
            })

        if status['DEX'] >= 12 and status['WIL'] >= 12:
            available_classes.append({
                'name': '실루엣',
                'description': '민첩과 의지로 승부하는 그림자 같은 존재',
                'requirements': {
                    'DEX': 12,
                    'WIL': 12
                },
                'bonuses': {
                    'DEX': 2,
                    'WIL': 2,
                    'dice_bonus': '은신/곡예 판정 +1'
                }
            })

        if status['WIL'] >= 13 and status['INT'] >= 11:
            available_classes.append({
                'name': '바인더',
                'description': '강력한 의지로 초자연적 존재를 구속하는 구속술사',
                'requirements': {
                    'WIL': 13,
                    'INT': 11
                },
                'bonuses': {
                    'WIL': 3,
                    'INT': 1,
                    'dice_bonus': '구속/제어 판정 +1'
                }
            })

        if status['INT'] >= 13:
            available_classes.append({
                'name': '렉쳐러',
                'description': '깊은 지식을 가르치고 전파하는 교육자',
                'requirements': {
                    'INT': 13
                },
                'bonuses': {
                    'INT': 3,
                    'dice_bonus': '지식/교육 판정 +1'
                }
            })

        return available_classes

# 사용 예시:
"""
SPREADSHEET_ID = '여기에_스프레드시트_ID_입력'
character_manager = CharacterManager(SPREADSHEET_ID)

# 캐릭터 정보 조회
character = character_manager.get_character("user123")

# 캐릭터 정보 업데이트
updates = {
    'galleons': 100,
    'current_hp': 80,
    'status': {
        'INT': 12,
        'STR': 15
    }
}
character_manager.update_character("user123", updates)

# 체력 회복
character_manager.heal_character("user123", 20)

# 갈레온 추가
character_manager.add_galleons("user123", 5)

# 출석 횟수 증가
character_manager.increment_attendance("user123")
"""

# 캐릭터 시트에 대한 추가 설정
def set_character_sheet_format(spreadsheet_id):
    gc = gspread.authorize(Credentials.from_service_account_file('credentials.json'))
    sheet = gc.open_by_key(spreadsheet_id).worksheet('Characters')
    
    # 캐릭터 시트의 각 열에 대한 포맷 설정
    column_formats = {
        'current_hp': {
            '75% 이상': 'green',
            '25% 이하': 'red',
            '기타': 'yellow'
        },
        'INT': {
            '20 이상': 'dark_green',
            '15-19': 'light_green',
            '10-14': 'white',
            '5-9': 'light_red',
            '0-4': 'dark_red'
        },
        'WIL': {
            '20 이상': 'dark_green',
            '15-19': 'light_green',
            '10-14': 'white',
            '5-9': 'light_red',
            '0-4': 'dark_red'
        },
        'CHA': {
            '20 이상': 'dark_green',
            '15-19': 'light_green',
            '10-14': 'white',
            '5-9': 'light_red',
            '0-4': 'dark_red'
        },
        'DEX': {
            '20 이상': 'dark_green',
            '15-19': 'light_green',
            '10-14': 'white',
            '5-9': 'light_red',
            '0-4': 'dark_red'
        },
        'STR': {
            '20 이상': 'dark_green',
            '15-19': 'light_green',
            '10-14': 'white',
            '5-9': 'light_red',
            '0-4': 'dark_red'
        },
        'MAG': {
            '20 이상': 'dark_green',
            '15-19': 'light_green',
            '10-14': 'white',
            '5-9': 'light_red',
            '0-4': 'dark_red'
        }
    }
    
    for column, formats in column_formats.items():
        for condition, color in formats.items():
            if column == 'current_hp':
                condition_parts = condition.split()
                min_value = int(condition_parts[0].replace('%', ''))
                max_value = int(condition_parts[2].replace('%', ''))
                sheet.conditional_format(
                    f'{column}2:{column}{sheet.row_count}',
                    {
                        'type': 'NUMBER_RANGE',
                        'min': min_value,
                        'max': max_value,
                        'format': {
                            'backgroundColor': {
                                'red': 0,
                                'green': 1 if color == 'green' else 0,
                                'blue': 0 if color == 'green' else 1
                            }
                        }
                    }
                )
            else:
                sheet.conditional_format(
                    f'{column}2:{column}{sheet.row_count}',
                    {
                        'type': 'NUMBER_RANGE',
                        'min': int(condition.split()[0]),
                        'max': int(condition.split()[2]),
                        'format': {
                            'backgroundColor': {
                                'red': 0,
                                'green': 1 if color == 'green' else 0,
                                'blue': 0 if color == 'green' else 1
                            }
                        }
                    }
                )

# 캐릭터 시트 포맷 설정
set_character_sheet_format(SPREADSHEET_ID)














