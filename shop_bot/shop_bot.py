from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime
import time

class ShopSystem:
    def __init__(self, spreadsheet_id, bank):
        self.spreadsheet_id = spreadsheet_id
        self.shop_items = {}
        self.bank = bank
        self.custom_keywords = {}
        self.last_update = 0
        self.update_interval = 60  # 60초마다 시트 확인
        self.gc = self._connect_to_sheets()
        self.load_shop_data()
        
    def _connect_to_sheets(self):
        """구글 시트 연결"""
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = Credentials.from_service_account_file(
            'credentials.json',
            scopes=scopes
        )
        return gspread.authorize(credentials)

    def should_update(self):
        """시트 업데이트가 필요한지 확인"""
        now = time.time()
        if now - self.last_update > self.update_interval:
            self.last_update = now
            return True
        return False

    def load_shop_data(self):
        """시트에서 데이터 로드"""
        try:
            spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
            
            # 키워드 시트 로드
            try:
                keyword_sheet = spreadsheet.worksheet('키워드')
                keyword_data = keyword_sheet.get_all_records()
                
                # 기존 키워드 초기화
                self.custom_keywords = {}
                
                for row in keyword_data:
                    if all(key in row for key in ['키워드', '설명']):
                        keyword = row['키워드'].strip().lower()
                        self.custom_keywords[keyword] = {
                            "owner_id": row.get('등록자ID', 'SHEET'),  # 시트 입력은 'SHEET'로 표시
                            "description": row['설명'],
                            "created_at": row.get('등록시간', '날짜 정보 없음')
                        }
            except Exception as e:
                print(f"키워드 시트 로드 중 오류: {str(e)}")

            # 상점 아이템 시트 로드
            try:
                items_sheet = spreadsheet.worksheet('상점')
                items_data = items_sheet.get_all_records()
                
                # 기존 아이템 초기화
                self.shop_items = {}
                
                for row in items_data:
                    if all(key in row for key in ['이름', '가격', '설명', '사용가능여부']):
                        item_name = row['이름'].strip()
                        # 체크박스가 체크된 아이템만 로드 (TRUE 또는 True 또는 checked)
                        if str(row['사용가능여부']).upper() in ['TRUE', 'CHECKED', '1']:
                            self.shop_items[item_name] = {
                                "price": int(row['가격']),
                                "description": row['설명'],
                                "category": row.get('카테고리', '기타')
                            }
            except Exception as e:
                print(f"상점 아이템 시트 로드 중 오류: {str(e)}")

        except Exception as e:
            print(f"시트 데이터 로드 중 오류: {str(e)}")

    def get_keyword_info(self, keyword):
        """키워드 정보 반환 (필요시 시트 업데이트)"""
        if self.should_update():
            self.load_shop_data()
        return self.custom_keywords.get(keyword.lower())

    def get_all_keywords(self):
        """모든 키워드 목록 반환 (필요시 시트 업데이트)"""
        if self.should_update():
            self.load_shop_data()
        return list(self.custom_keywords.keys())

    def add_custom_keyword(self, user_id, keyword, description):
        """키워드 추가"""
        keyword = keyword.lower()
        if keyword in self.shop_items:
            return False, "이미 존재하는 상점 아이템과 같은 이름은 사용할 수 없습니다."
            
        if keyword in self.custom_keywords:
            return False, "이미 존재하는 키워드입니다."
            
        try:
            sheet = self.gc.open_by_key(self.spreadsheet_id).worksheet('키워드')
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 시트에 추가
            sheet.append_row([
                now,           # 등록시간
                str(user_id),  # 등록자ID
                keyword,       # 키워드
                description    # 설명
            ])
            
            # 메모리에 추가
            self.custom_keywords[keyword] = {
                "owner_id": str(user_id),
                "description": description,
                "created_at": now
            }
            
            return True, f"키워드 '{keyword}'가 추가되었습니다."
            
        except Exception as e:
            print(f"키워드 추가 중 오류: {str(e)}")
            return False, "키워드 추가 중 오류가 발생했습니다."

    def remove_keyword(self, user_id, keyword):
        """키워드 제거"""
        keyword = keyword.lower()
        if keyword not in self.custom_keywords:
            return False, "존재하지 않는 키워드입니다."
        
        # 시트에서 직접 입력한 키워드는 삭제 불가
        if self.custom_keywords[keyword]["owner_id"] == 'SHEET':
            return False, "시트에서 직접 입력한 키워드는 봇으로 삭제할 수 없습니다."
    
        if str(self.custom_keywords[keyword]["owner_id"]) != str(user_id):
            return False, "자신이 등록한 키워드만 제거할 수 있습니다."
        
        try:
            sheet = self.gc.open_by_key(self.spreadsheet_id).worksheet('키워드')
            cell = sheet.find(keyword)
            if cell:
                sheet.delete_row(cell.row)
            
            del self.custom_keywords[keyword]
            return True, f"키워드 '{keyword}'가 제거되었습니다."
        
        except Exception as e:
            print(f"키워드 제거 중 오류: {str(e)}")
            return False, "키워드 제거 중 오류가 발생했습니다."
        
    def _update_items(self):
        """상점 아이템 목록 갱신"""
        current_time = datetime.now().timestamp()
        if current_time - self.last_update > self.update_interval:
            try:
                sheet = self.gc.open_by_key(self.spreadsheet_id).worksheet('상점')
                # 첫 번째 행(헤더) 제외하고 모든 데이터 가져오기
                data = sheet.get_all_values()[1:]
                
                # 사용 가능한 아이템만 필터링
                self.items = []
                for row in data:
                    if len(row) >= 4 and row[3].upper() == 'TRUE':
                        name, price, desc, _ = row[:4]
                        self.items.append({
                            'name': name,
                            'price': int(price),
                            'description': desc
                        })
                
                self.last_update = current_time
            except Exception as e:
                print(f"상점 데이터 갱신 중 오류: {str(e)}")

    def list_items(self):
        """상점 물품 목록 표시"""
        self._update_items()
        
        if not self.items:
            return "현재 판매 중인 물품이 없습니다."

        result = ["🏪 마법 상점 물품 목록 🏪\n"]
        
        for item in self.items:
            result.append(
                f"\n• {item['name']} - {item['price']}G"
                f"\n  └ {item['description']}"
            )

        return ''.join(result)

    def purchase_item(self, user_id, item_name):
        """물품 구매"""
        if self.should_update():
            self.load_shop_data()
        
        # 아이템 검색
        if item_name not in self.shop_items:
            return "해당 물품을 찾을 수 없습니다."

        item = self.shop_items[item_name]
        
        # 성인전용 아이템 체크
        if item.get('category') == '성인전용':
            character = self.get_character(user_id)
            if not character or not character.get('is_adult'):
                return "성인기간 전용 아이템입니다!"

        # 잔액 확인
        user_balance = self.bank.get_balance(user_id)
        if user_balance < item['price']:
            return "갈레온이 부족합니다!"

        # 아이템 효과 적용
        effects = {
            '강화타격 책': lambda char: self.apply_combat_bonus(char, 'attack', 5, '1d6'),
            '회피 강화책': lambda char: self.apply_combat_bonus(char, 'dodge', 5, '1d6'),
            '마력 증폭책': lambda char: self.apply_status_bonus(char, 'MAG', 10),
            '보호마법 로브': lambda char: self.apply_status_bonus(char, 'DEX', 10),
            '고급 회복 물약': lambda char: self.apply_healing(char, 10)
        }

        if item_name in effects:
            character = self.get_character(user_id)
            effects[item_name](character)

        # 구매 처리
        self.bank.withdraw(user_id, item['price'])
        return f"{item_name}을(를) 구매했습니다!"

    def apply_combat_bonus(self, character, stat_type, base_bonus, dice_bonus):
        """전투 보너스 적용"""
        import random
        
        if stat_type not in character['combat_stats']:
            character['combat_stats'][stat_type] = {}
        
        # 기본 보너스 적용
        character['combat_stats'][stat_type]['base_bonus'] = base_bonus
        
        # 주사위 보너스 적용 (1d6)
        if dice_bonus == '1d6':
            dice_result = random.randint(1, 6)
            character['combat_stats'][stat_type]['dice_bonus'] = dice_result
            
        self.update_character(character['id'], {'combat_stats': character['combat_stats']})
        
    def apply_status_bonus(self, character, stat_type, bonus):
        """스테이터스 보너스 적용"""
        if 'status' not in character:
            character['status'] = {}
            
        if stat_type not in character['status']:
            character['status'][stat_type] = 0
            
        character['status'][stat_type] += bonus
        self.update_character(character['id'], {'status': character['status']})

    def apply_healing(self, character, amount):
        """캐릭터 HP 회복"""
        current_hp = character.get('current_hp', 0)
        max_hp = character.get('max_hp', 100)
        new_hp = min(current_hp + amount, max_hp)
        character['current_hp'] = new_hp
        self.save_character(character)
        return f"HP가 {amount} 회복되었습니다! (현재 HP: {new_hp}/{max_hp})"

    def get_shop_list(self):
        """상점 아이템 목록 반환"""
        if self.should_update():
            self.load_shop_data()
        
        # 카테고리별로 아이템 정리
        categorized_items = {}
        for item_name, item_info in self.shop_items.items():
            category = item_info['category']
            if category not in categorized_items:
                categorized_items[category] = []
            categorized_items[category].append({
                'name': item_name,
                'price': item_info['price'],
                'description': item_info['description']
            })
        
        # 결과 문자열 생성
        result = "🏪 상점 아이템 목록\n\n"
        for category, items in sorted(categorized_items.items()):
            result += f"📦 {category}\n"
            for item in sorted(items, key=lambda x: x['price']):
                result += f"• {item['name']} ({item['price']}G) - {item['description']}\n"
            result += "\n"
        
        return result





