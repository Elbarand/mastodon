from spells import Revelio, SpellResult
from clue import Clue
import random

class ClueSystem:
    def __init__(self, character_manager, clue_database):
        self.character_manager = character_manager
        self.clue_database = clue_database
        self.revelio = Revelio()
        
        # 단서 난이도 등급
        self.DIFFICULTY_LEVELS = {
            "쉬움": 10,
            "보통": 15,
            "어려움": 20,
            "매우 어려움": 25
        }
        
    def search_for_clues(self, user_id, location_id, difficulty="보통"):
        """레벨리오 주문을 사용하여 단서 탐색"""
        character = self.character_manager.get_character(user_id)
        if not character:
            return "캐릭터 정보를 찾을 수 없습니다."
            
        if character['current_mana'] < 5:
            return "마나가 부족합니다. (필요 마나: 5)"
            
        # 주문 시전 및 결과 처리
        spell_result = self.revelio.cast(character, clue_difficulty=self.DIFFICULTY_LEVELS[difficulty])
        new_mana = character['current_mana'] - spell_result['mana_cost']
        self.character_manager.update_character(user_id, {'current_mana': new_mana})
        
        # 발견한 단서 처리
        discovered_clue = self._process_clue_discovery(
            location_id, 
            spell_result['result'],
            character['id']
        )
        
        return self._format_result_message(
            spell_result,
            discovered_clue,
            character['name'],
            new_mana
        )

    def _process_clue_discovery(self, location_id, spell_result, character_id):
        """주문 결과에 따른 단서 발견 처리"""
        available_clues = self.clue_database.get_location_clues(location_id)
        
        if not available_clues:
            return None
            
        if spell_result == SpellResult.CRITICAL_SUCCESS:
            # 특수 또는 핵심 단서 우선 선택
            special_clues = [c for c in available_clues if c.clue_type in ['특수', '핵심']]
            clue = random.choice(special_clues) if special_clues else random.choice(available_clues)
        elif spell_result == SpellResult.SUCCESS:
            # 일반 단서 선택
            normal_clues = [c for c in available_clues if c.clue_type == '일반']
            clue = random.choice(normal_clues) if normal_clues else random.choice(available_clues)
        elif spell_result == SpellResult.CRITICAL_FAIL:
            # 잘못된 단서 생성
            return Clue(
                title="잘못된 단서",
                description="완전히 잘못된 결론에 도달했습니다...",
                location_id=location_id,
                clue_type="오류"
            )
        else:
            return None
            
        if clue:
            clue.mark_as_discovered(character_id)
            
        return clue

    def _format_result_message(self, spell_result, clue, character_name, new_mana):
        """결과 메시지 포맷팅"""
        messages = [
            f"🪄 {character_name}의 레벨리오 주문! (주사위: {spell_result['roll']})",
            f"총 주문력: {spell_result['total_power']} vs 난이도: {spell_result['difficulty']}",
            f"마나 소모: {spell_result['mana_cost']} (남은 마나: {new_mana})"
        ]
        
        if clue:
            messages.extend([
                f"\n📜 발견한 단서: {clue.title}",
                f"유형: {clue.clue_type}",
                f"내용: {clue.description}"
            ])
        else:
            messages.append("\n❌ 단서를 발견하지 못했습니다.")
            
        return "\n".join(messages)




