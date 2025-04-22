from datetime import datetime
import random
from typing import Dict, List, Tuple
from google.oauth2.service_account import Credentials
import gspread

class BattleState:
    def __init__(self, teams: Dict[str, List[str]], initiative_order: List[str]):
        self.teams = teams  # {team_name: [user_ids]}
        self.initiative_order = initiative_order  # [user_ids] in turn order
        self.current_turn_index = 0
        self.round = 1
        self.active = True
        self.characters = {}  # {user_id: character_data}

class CombatSystem:
    def __init__(self, spreadsheet_id, character_manager):
        self.spreadsheet_id = spreadsheet_id
        self.character_manager = character_manager
        self.gc = self._init_google_sheets()
        self.active_battles = {}
        
        # 기본 상수
        self.HEAL_BASE_CHANCE = 0.9  # 기본 치료 성공률
        self.DISTANCE_PENALTY = 0.15  # 거리당 성공률 감소
        self.MAX_HEAL_DISTANCE = 3    # 최대 치료 가능 거리
        
        self.load_combat_settings()

    def load_combat_settings(self):
        """전투 관련 설정을 스프레드시트에서 로드"""
        try:
            # 상태이상 효과 로드
            status_sheet = self.gc.open_by_key(self.spreadsheet_id).worksheet('상태이상')
            self.status_effects = {}
            for row in status_sheet.get_all_records():
                self.status_effects[row['상태이상']] = {
                    'description': row['설명'],
                    'duration': int(row['기본지속턴']),
                    'icon': row['아이콘'],
                    'effect_type': row['효과종류'],
                    'effect_value': float(row['효과수치'])
                }

            # 전투 메시지 템플릿 로드
            message_sheet = self.gc.open_by_key(self.spreadsheet_id).worksheet('전투메시지')
            self.message_templates = {}
            for row in message_sheet.get_all_records():
                self.message_templates[row['메시지키']] = {
                    'text': row['메시지내용'],
                    'variables': row['사용변수'].split(',') if row['사용변수'] else []
                }

        except Exception as e:
            print(f"전투 설정 로드 중 오류 발생: {e}")
            # 기본값 설정
            self.status_effects = {
                '중독': {
                    'description': '매 턴 시작시 HP 감소',
                    'duration': 3,
                    'icon': '☠️',
                    'effect_type': 'dot',
                    'effect_value': 5
                }
            }
            self.message_templates = {
                'battle_start': {'text': '⚔️ 전투가 시작되었습니다! ⚔️', 'variables': []},
                'attack': {'text': '{attacker}의 {attack_type} 공격!', 'variables': ['attacker', 'attack_type']}
            }

    def format_message(self, key: str, **kwargs) -> str:
        """메시지 템플릿 포맷팅"""
        template = self.message_templates.get(key)
        if not template:
            return f"메시지 템플릿 없음: {key}"
        
        try:
            return template['text'].format(**kwargs)
        except KeyError as e:
            return f"메시지 포맷팅 오류: {e}"

    def apply_status_effect(self, battle_id: str, target_id: str, status_name: str) -> str:
        """상태이상 효과 적용"""
        if battle_id not in self.active_battles:
            return "진행 중인 전투를 찾을 수 없습니다."

        battle = self.active_battles[battle_id]
        if target_id not in battle.characters:
            return "대상을 찾을 수 없습니다."

        effect = self.status_effects.get(status_name)
        if not effect:
            return f"알 수 없는 상태이상: {status_name}"

        # 상태이상 적용
        if 'status_effects' not in battle.characters[target_id]:
            battle.characters[target_id]['status_effects'] = {}

        battle.characters[target_id]['status_effects'][status_name] = {
            'duration': effect['duration'],
            'effect_type': effect['effect_type'],
            'effect_value': effect['effect_value']
        }

        return self.format_message('status_applied', 
            target=target_id,
            status=status_name,
            icon=effect['icon'],
            description=effect['description']
        )

    def process_status_effects(self, battle_id: str, character_id: str) -> List[str]:
        """턴 시작시 상태이상 효과 처리"""
        messages = []
        battle = self.active_battles[battle_id]
        character = battle.characters[character_id]
        
        if 'status_effects' not in character:
            return messages

        status_effects = character['status_effects'].copy()
        for status_name, effect in status_effects.items():
            base_effect = self.status_effects[status_name]
            
            # 효과 적용
            if effect['effect_type'] == 'dot':
                damage = effect['effect_value']
                character['current_hp'] = max(0, character['current_hp'] - damage)
                messages.append(self.format_message('status_damage',
                    target=character_id,
                    status=status_name,
                    icon=base_effect['icon'],
                    damage=damage
                ))

            # 지속시간 감소
            effect['duration'] -= 1
            if effect['duration'] <= 0:
                del character['status_effects'][status_name]
                messages.append(self.format_message('status_expired',
                    target=character_id,
                    status=status_name,
                    icon=base_effect['icon']
                ))

        return messages

    def _init_google_sheets(self):
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

    def roll_initiative(self, character) -> int:
        """민첩 기반 이니셔티브 굴리기"""
        return random.randint(1, 20) + character['DEX']

    def calculate_damage(self, attacker, defender, skill_type="normal"):
        """데미지 계산
        
        Args:
            attacker: 공격자 캐릭터 데이터
            defender: 방어자 캐릭터 데이터
            skill_type: 스킬 타입 ("normal", "magic", "special")
        
        Returns:
            (데미지, 크리티컬 여부)
        """
        # 기본 공격력 계산
        if skill_type == "magic":
            base_power = attacker['MAG']
            defense = defender['WIL']
        else:
            base_power = attacker['STR']
            defense = defender['DEX'] // 2
        
        # 기본 데미지 계산
        damage = self.BASE_DAMAGE + (base_power - defense)
        
        # 크리티컬 확률 계산 (DEX 기반)
        crit_chance = min(attacker['DEX'] * 0.01, 0.25)  # 최대 25%
        is_critical = random.random() < crit_chance
        
        if is_critical:
            damage *= self.CRIT_MULTIPLIER
            
        return max(1, int(damage)), is_critical

    def start_battle(self, teams: Dict[str, List[str]]) -> Tuple[str, str]:
        """전투 시작
        
        Args:
            teams: {"team_name": [user_ids]} 형식의 팀 구성
        """
        # 캐릭터 정보 검증 및 가져오기
        characters = {}
        for team_name, team_members in teams.items():
            for user_id in team_members:
                char = self.character_manager.get_character(user_id)
                if not char:
                    return None, f"{user_id}의 캐릭터 정보를 찾을 수 없습니다."
                if char['current_hp'] <= 0:
                    return None, f"{user_id}의 캐릭터가 전투불능 상태입니다."
                characters[user_id] = char

        # 이니셔티브 순서 결정
        initiative_rolls = {
            user_id: self.roll_initiative(char)
            for user_id, char in characters.items()
        }
        
        initiative_order = sorted(
            initiative_rolls.keys(),
            key=lambda x: initiative_rolls[x],
            reverse=True
        )

        # 전투 ID 생성 및 상태 저장
        battle_id = f"battle_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        battle_state = BattleState(teams, initiative_order)
        battle_state.characters = characters
        self.active_battles[battle_id] = battle_state

        # 전투 시작 메시지 생성
        message = ["⚔️ 전투가 시작되었습니다! ⚔️"]
        for team_name, team_members in teams.items():
            message.append(f"\n[{team_name}]")
            for user_id in team_members:
                char = characters[user_id]
                message.append(
                    f"👤 {user_id} (HP: {char['current_hp']}/{char['max_hp']})"
                )

        message.append("\n🎲 이니셔티브 순서:")
        for i, user_id in enumerate(initiative_order, 1):
            message.append(f"{i}. {user_id} ({initiative_rolls[user_id]})")

        message.append(f"\n👉 {initiative_order[0]}의 차례입니다.")

        return battle_id, "\n".join(message)

    def process_attack(self, battle_id: str, user_id: str, target_id: str, attack_type: str = "physical") -> str:
        """공격 처리
        
        Args:
            battle_id: 전투 ID
            user_id: 공격자 ID
            target_id: 대상 ID
            attack_type: "physical" 또는 "magical"
        """
        if battle_id not in self.active_battles:
            return "진행 중인 전투를 찾을 수 없습니다."

        battle = self.active_battles[battle_id]
        
        # 턴 확인
        current_turn = battle.initiative_order[battle.current_turn_index]
        if user_id != current_turn:
            return "아직 당신의 차례가 아닙니다."

        # 대상이 같은 팀인지 확인
        attacker_team = None
        target_team = None
        for team_name, members in battle.teams.items():
            if user_id in members:
                attacker_team = team_name
            if target_id in members:
                target_team = team_name
        
        if attacker_team == target_team:
            return "같은 팀원을 공격할 수 없습니다."

        # 공격 처리
        attacker = battle.characters[user_id]
        defender = battle.characters[target_id]

        # 데미지 계산
        if attack_type == "magical":
            damage, is_critical = self.calculate_damage(attacker, defender, "magic")
            attack_stat = "마력"
        else:
            damage, is_critical = self.calculate_damage(attacker, defender, "normal")
            attack_stat = "물리"

        # HP 감소
        new_hp = max(0, defender['current_hp'] - damage)
        self.character_manager.update_character(target_id, {'current_hp': new_hp})
        battle.characters[target_id]['current_hp'] = new_hp

        # 다음 턴으로
        battle.current_turn_index = (battle.current_turn_index + 1) % len(battle.initiative_order)
        if battle.current_turn_index == 0:
            battle.round += 1

        # 메시지 생성
        message = [
            f"💥 {user_id}의 {'치명적인 ' if is_critical else ''}{attack_stat} 공격!",
            f"🎯 {target_id}에게 {damage}의 피해를 입혔습니다!"
        ]

        # 전투 상태 출력
        message.append("\n현재 상태:")
        for team_name, members in battle.teams.items():
            message.append(f"\n[{team_name}]")
            for member_id in members:
                char = battle.characters[member_id]
                message.append(
                    f"👤 {member_id}: {char['current_hp']}/{char['max_hp']} HP"
                )

        # 전투 종료 체크
        if self.check_battle_end(battle):
            winner_team = self.get_winner_team(battle)
            message.append(f"\n🏆 전투 종료! {winner_team} 팀의 승리!")
            del self.active_battles[battle_id]
        else:
            next_turn = battle.initiative_order[battle.current_turn_index]
            message.append(f"\n👉 {next_turn}의 차례입니다.")

        return "\n".join(message)

    def check_battle_end(self, battle: BattleState) -> bool:
        """전투 종료 조건 체크"""
        for team_name, members in battle.teams.items():
            all_defeated = all(
                battle.characters[member_id]['current_hp'] <= 0
                for member_id in members
            )
            if all_defeated:
                return True
        return False

    def get_winner_team(self, battle: BattleState) -> str:
        """승리 팀 확인"""
        for team_name, members in battle.teams.items():
            if any(battle.characters[member_id]['current_hp'] > 0 for member_id in members):
                return team_name
        return "무승부"

    def end_battle(self, battle_id: str) -> str:
        """전투 강제 종료"""
        if battle_id in self.active_battles:
            battle = self.active_battles[battle_id]
            teams_str = " vs ".join(battle.teams.keys())
            del self.active_battles[battle_id]
            return f"전투가 강제 종료되었습니다. ({teams_str})"
        return "진행 중인 전투를 찾을 수 없습니다."

    def can_join_battle(self, user_id: str) -> Tuple[bool, str]:
        """전투 참여 가능 여부 확인"""
        character = self.character_manager.get_character(user_id)
        if not character:
            return False, "캐릭터 정보를 찾을 수 없습니다."
        if character['current_hp'] <= 0:
            return False, "전투불능 상태입니다. 치료가 필요합니다."
        return True, ""

    def calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """두 위치 사이의 거리 계산"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])  # Manhattan distance

    def heal_target(self, battle_id: str, healer_id: str, target_id: str) -> str:
        """대상 치료 시도"""
        if battle_id not in self.active_battles:
            return "진행 중인 전투를 찾을 수 없습니다."
            
        battle = self.active_battles[battle_id]
        
        # 치료자 검증
        if healer_id not in battle.characters:
            return "치료자를 찾을 수 없습니다."
        healer = battle.characters[healer_id]
        
        # 대상 검증
        if target_id not in battle.characters:
            return "치료 대상을 찾을 수 없습니다."
        target = battle.characters[target_id]
        
        # 치료자가 행동 가능한 상태인지 확인
        if self.is_incapacitated(healer):
            return "치료자가 행동불능 상태입니다."
            
        # 이미 최대 체력인 경우
        if target['current_hp'] >= target['max_hp']:
            return "대상이 이미 최대 체력입니다."

        # 거리에 따른 성공률 계산
        distance = self.calculate_distance(
            battle.positions[healer_id],
            battle.positions[target_id]
        )
        
        if distance > self.MAX_HEAL_DISTANCE:
            return "대상이 치료 가능 범위를 벗어났습니다."
            
        success_chance = max(0.1, 
            self.HEAL_BASE_CHANCE - (distance * self.DISTANCE_PENALTY)
        )
        
        # 치료량 계산 (지능과 의지 기반)
        base_heal = (healer['INT'] + healer['WIL']) // 2
        
        # 치료 시도
        if random.random() < success_chance:
            # 치료 성공
            heal_amount = int(base_heal * success_chance)  # 거리에 따라 치료량도 감소
            new_hp = min(
                target['max_hp'],
                target['current_hp'] + heal_amount
            )
            
            # HP 업데이트
            self.character_manager.update_character(
                target_id,
                {'current_hp': new_hp}
            )
            battle.characters[target_id]['current_hp'] = new_hp
            
            return self.format_message('heal_success',
                healer=healer_id,
                target=target_id,
                amount=heal_amount,
                distance=distance
            )
        else:
            # 치료 실패
            return self.format_message('heal_fail',
                healer=healer_id,
                target=target_id,
                distance=distance
            )

    def self_heal(self, battle_id: str, character_id: str) -> str:
        """자가 치료"""
        if battle_id not in self.active_battles:
            return "진행 중인 전투를 찾을 수 없습니다."
            
        battle = self.active_battles[battle_id]
        
        if character_id not in battle.characters:
            return "캐릭터를 찾을 수 없습니다."
        
        character = battle.characters[character_id]
        
        # 행동 가능 상태 확인
        if self.is_incapacitated(character):
            return "행동불능 상태입니다."
            
        # 이미 최대 체력인 경우
        if character['current_hp'] >= character['max_hp']:
            return "이미 최대 체력입니다."
            
        # 자가 치료량 계산 (의지 기반)
        heal_amount = character['WIL'] // 3  # 자가 치료는 일반 치료보다 효과가 낮음
        
        new_hp = min(
            character['max_hp'],
            character['current_hp'] + heal_amount
        )
        
        # HP 업데이트
        self.character_manager.update_character(
            character_id,
            {'current_hp': new_hp}
        )
        battle.characters[character_id]['current_hp'] = new_hp
        
        return self.format_message('self_heal',
            character=character_id,
            amount=heal_amount
        )

    def is_incapacitated(self, character: Dict) -> bool:
        """행동불능 상태인지 확인"""
        if character['current_hp'] <= 0:
            return True
            
        # 기절 등의 상태이상 확인
        if 'status_effects' in character:
            for status, effect in character['status_effects'].items():
                if effect['effect_type'] == 'stun':
                    return True
                    
        return False


